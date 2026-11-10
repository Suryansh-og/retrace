// ============================================================
// RETRACE — DASHBOARD
// ============================================================

let applicationResultsPage = 1;

const APPLICATION_PAGE_SIZE = 10;

let currentApplicationResults = [];
let currentApplicationContainer = null;
let currentApplicationName = "";

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();

    // Initialize collector controls
    initializeCollectorControls();

    // Initialize sidebar collector status
    updateSidebarCollectorStatus();

    const refreshButton = document.getElementById("refresh-dashboard");

    if (refreshButton) {
        refreshButton.addEventListener("click", async () => {
            refreshButton.classList.add("is-refreshing");

            await loadDashboard();
            await updateCollectorStatus();
            await updateSidebarCollectorStatus();

            window.setTimeout(
                () => refreshButton.classList.remove("is-refreshing"),
                450
            );
        });
    }
});

// ============================================================
// MAIN DASHBOARD
// ============================================================

async function fetchDashboardData(url, sectionName) {

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(
            `${sectionName} API returned HTTP ${response.status}`
        );
    }

    return response.json();

}


async function loadDashboard() {

    try {

        // --------------------------------------------------------
        // SUMMARY
        // --------------------------------------------------------

        const summary = await fetchDashboardData(
            "/api/summary",
            "Summary"
        );

        document.getElementById("total-events").textContent =
            summary.total_events ?? 0;

        document.getElementById("total-sessions-secondary").textContent =
            summary.total_sessions ?? 0;

        document.getElementById("total-signals").textContent =
            summary.behavior_signals ?? 0;


        // --------------------------------------------------------
        // APPLICATION USAGE
        // --------------------------------------------------------

        const usage = await fetchDashboardData(
            "/api/usage",
            "Application usage"
        );

        renderUsage(usage);


        // --------------------------------------------------------
        // TIMELINE
        // --------------------------------------------------------

        const timeline = await fetchDashboardData(
            "/api/timeline",
            "Timeline"
        );

        renderTimeline(timeline);


        // --------------------------------------------------------
        // SESSIONS
        // --------------------------------------------------------

        const sessions = await fetchDashboardData(
            "/api/sessions",
            "Sessions"
        );

        renderSessions(sessions);


        // --------------------------------------------------------
        // BEHAVIOR SIGNALS
        // --------------------------------------------------------

        const signals = await fetchDashboardData(
            "/api/signals",
            "Behavior signals"
        );

        renderSignals(signals);


        // --------------------------------------------------------
        // RELATIONSHIPS
        // --------------------------------------------------------

        await loadRelationships();

    }

    catch (error) {

        console.error("Dashboard error:", error);

    }

}


// ============================================================
// APPLICATION USAGE
// ============================================================

function renderUsage(usage) {

    const container = document.getElementById("usage");

    if (!container) return;

    container.innerHTML = "";

    if (!usage || usage.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No application usage data available.
            </div>
        `;

        return;
    }

    const maxDuration = Math.max(
        ...usage.map(item => Number(item.duration) || 0),
        1
    );

    usage.forEach((item, index) => {

        const application = escapeHtml(item.application ?? "Unknown");
        const duration = Number(item.duration) || 0;

        const formattedDuration = formatUsageDuration(duration);

        const width = Math.max(
            1.5,
            duration / maxDuration * 100
        );

        const element = document.createElement("div");

        element.className = "usage-item reveal-item";
        element.style.setProperty("--item-index", index);

        element.innerHTML = `
            <div class="usage-header">
                <span class="usage-app">${application}</span>
                <span class="usage-time">${formattedDuration}</span>
            </div>

            <div
                class="usage-bar"
                role="progressbar"
                aria-label="${application} duration"
                aria-valuemin="0"
                aria-valuemax="${maxDuration}"
                aria-valuenow="${duration}"
            >
                <div
                    class="usage-fill"
                    style="--bar-width:${width}%"
                ></div>
            </div>
        `;

        container.appendChild(element);
    });

}


// ============================================================
// TIMELINE
// ============================================================

function renderTimeline(timeline) {
    const container = document.getElementById("timeline");

    if (!container) return;

    container.innerHTML = "";

    if (!timeline || timeline.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No recent activity has been recorded.
            </div>
        `;
        return;
    }

    [...timeline].reverse().forEach((event, index) => {
        const element = document.createElement("button");

        element.type = "button";
        element.className = "recent-event reveal-item";
        element.style.setProperty("--item-index", index);

        const parsedDate = event.timestamp
            ? new Date(event.timestamp)
            : null;

        const time = parsedDate && !isNaN(parsedDate.getTime())
            ? parsedDate.toLocaleTimeString("en-IN", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            })
            : "Time unavailable";

        element.innerHTML = `
            <span class="recent-event-rail"><i></i></span>

            <span class="recent-event-body">
                <span class="recent-event-top">
                    <strong>${escapeHtml(event.application || "Unknown")}</strong>
                    <time>${escapeHtml(time)}</time>
                </span>

                <span class="recent-event-context">
                    ${escapeHtml(event.context || "No context captured")}
                </span>

                <span class="recent-event-meta">
                    <span>SESSION ${escapeHtml(event.session_id ?? "—")}</span>
                    <span>EVENT #${escapeHtml(event.id ?? "—")}</span>
                </span>
            </span>

            <span class="recent-event-arrow">↗</span>
        `;

        const eventId = Number(event.id);
        const hasValidEventId =
            event.id !== null &&
            event.id !== undefined &&
            String(event.id).trim() !== "" &&
            Number.isInteger(eventId) &&
            eventId > 0;

        element.disabled = !hasValidEventId;

        if (hasValidEventId) {
            element.addEventListener("click", () => showTrace(eventId));
        }

        container.appendChild(element);
    });
}

// ============================================================
// SESSIONS
// ============================================================


function renderSessions(sessions) {

    const container =
        document.getElementById("sessions");

    if (!container) return;

    container.innerHTML = "";

    if (!sessions || sessions.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No sessions available.
            </div>
        `;

        return;
    }

    sessions.forEach(session => {

        const element =
            document.createElement("div");

        element.className =
            "session-card reveal-item";

        const sessionId = Number(session.id);

        const hasValidSessionId =
            session.id !== null &&
            session.id !== undefined &&
            String(session.id).trim() !== "" &&
            Number.isInteger(sessionId) &&
            sessionId > 0;

        if (hasValidSessionId) {
            element.onclick = () =>
                showSession(sessionId);
        }

        element.innerHTML = `

            <div class="session-card-header">

                <span>
                    Session ${escapeHtml(session.id ?? "N/A")}
                </span>

                <span class="session-arrow">
                    →
                </span>

            </div>

            <div class="session-info">

                <span>
                    ${escapeHtml(session.event_count ?? 0)} events
                </span>

                <span>
                    ${escapeHtml(session.duration ?? 0)}s
                </span>

            </div>

        `;

        container.appendChild(element);

    });

}


// ============================================================
// BEHAVIOR SIGNALS
// ============================================================


function renderSignals(signals) {

    const container =
        document.getElementById("signals");

    if (!container) return;

    container.innerHTML = "";

    if (!signals || signals.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No behavioral signals detected.
            </div>
        `;

        return;
    }

    signals.forEach(signal => {

        const element =
            document.createElement("div");

        element.className =
            "signal-card reveal-item";

        const eventId = Number(signal.event_id);

        const hasValidEventId =
            signal.event_id !== null &&
            signal.event_id !== undefined &&
            String(signal.event_id).trim() !== "" &&
            Number.isInteger(eventId) &&
            eventId > 0;

        element.innerHTML = `

            <div class="signal-pattern">

                ${escapeHtml(signal.pattern ?? "Unknown pattern")}

            </div>

            <div class="signal-details">

                Session ${escapeHtml(signal.session_id ?? "N/A")}

                · Observed ${escapeHtml(signal.count ?? 0)} time${Number(signal.count) !== 1 ? "s" : ""}

            </div>

            <button
                class="trace-button"
                ${hasValidEventId ? `onclick="showTrace(${eventId})"` : "disabled"}
            >
                Trace
            </button>

        `;

        container.appendChild(element);

    });

}



// ============================================================
// SESSION DETAILS
// ============================================================

async function showSession(sessionId) {

    const numericSessionId = Number(sessionId);

    if (
        sessionId === null ||
        sessionId === undefined ||
        String(sessionId).trim() === "" ||
        !Number.isInteger(numericSessionId) ||
        numericSessionId <= 0
    ) {
        console.warn("Invalid session ID:", sessionId);
        return;
    }

    try {

        const response =
            await fetch(`/api/sessions/${numericSessionId}/events`);

        if (!response.ok) {
            throw new Error(`Session API returned ${response.status}`);
        }

        const events =
            await response.json();

        const panel =
            document.getElementById("trace-panel");

        if (!panel) return;

        const sessionEvents = Array.isArray(events) ? events : [];

        panel.style.display = "block";

        panel.innerHTML = `

            <div class="trace-title">
                Session ${numericSessionId}
            </div>

            <div class="trace-section">

                <div class="trace-section-title">
                    Session Timeline
                </div>

                ${sessionEvents.length === 0

                ? `
                        <div class="trace-context">
                            No events found.
                        </div>
                    `

                : renderTraceEvents(sessionEvents)

            }

            </div>

        `;

        panel.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

    catch (error) {

        console.error(
            "Session error:",
            error
        );

    }

}


// ============================================================
// RELATIONSHIPS
// ============================================================

async function loadRelationships() {

    const container =
        document.getElementById("relationships-container");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            Building event graph...
        </div>
    `;

    try {

        const response =
            await fetch("/api/relationships");

        if (!response.ok) {
            throw new Error(
                `Relationships API returned ${response.status}`
            );
        }

        const relationships =
            await response.json();


        // ------------------------------------------------
        // CHECK DATA
        // ------------------------------------------------

        if (
            !Array.isArray(relationships) ||
            relationships.length === 0
        ) {

            container.innerHTML = `
                <div class="empty-state">
                    No event relationships available.
                </div>
            `;

            return;
        }

        // ------------------------------------------------
        // RELATIONSHIPS TO DISPLAY
        // ------------------------------------------------

        const startInput = document.getElementById("graph-start-event");
        const endInput = document.getElementById("graph-end-event");

        const startValue = startInput?.value.trim() ?? "";
        const endValue = endInput?.value.trim() ?? "";

        const startId = startValue === "" ? -Infinity : Number(startValue);
        const endId = endValue === "" ? Infinity : Number(endValue);

        if (
            (startValue !== "" && (!Number.isInteger(startId) || startId < 1)) ||
            (endValue !== "" && (!Number.isInteger(endId) || endId < 1)) ||
            startId > endId
        ) {
            container.innerHTML = `
                <div class="empty-state">
                    Enter a valid start and last event ID.
                </div>
            `;
            return;
        }

        const graphRelationships = relationships
            .filter(r => {
                const fromId = Number(r.from_event);
                const toId = Number(r.to_event);

                return (
                    Number.isInteger(fromId) &&
                    fromId > 0 &&
                    Number.isInteger(toId) &&
                    toId > 0 &&
                    fromId >= startId &&
                    fromId <= endId &&
                    toId >= startId &&
                    toId <= endId
                );
            })
            .slice(0, 100);

        if (graphRelationships.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    No relationships found in this event range.
                    Try a wider range or press Reset.
                </div>
            `;
            return;
        }

        // ------------------------------------------------
        // UNIQUE EVENT IDS
        // ------------------------------------------------

        const nodeIds = [];

        graphRelationships.forEach(r => {

            const fromId = Number(r.from_event);
            const toId = Number(r.to_event);

            if (!nodeIds.includes(fromId)) {
                nodeIds.push(fromId);
            }

            if (!nodeIds.includes(toId)) {
                nodeIds.push(toId);
            }

        });

        // ------------------------------------------------
        // GET EVENT DETAILS
        // ------------------------------------------------

        const eventMap = {};

        const eventDetails =
            await Promise.all(

                nodeIds.map(async id => {

                    try {

                        const result =
                            await fetch(
                                `/api/trace/${id}`
                            );

                        if (!result.ok) {
                            return null;
                        }

                        const data =
                            await result.json();

                        return data.target;

                    }
                    catch (error) {

                        console.error(
                            `Could not load event ${id}`,
                            error
                        );

                        return null;

                    }

                })

            );

        eventDetails.forEach(event => {

            if (event) {
                eventMap[event.id] = event;
            }

        });


        // ------------------------------------------------
        // GRAPH SIZE
        // ------------------------------------------------

        const width = 900;

        const rowHeight = 110;

        const height =
            Math.max(
                500,
                Math.ceil(
                    nodeIds.length / 2
                ) * rowHeight + 100
            );


        // ------------------------------------------------
        // NODE POSITIONS
        // ------------------------------------------------

        const positions = {};

        nodeIds.forEach((id, index) => {

            const column =
                index % 2;

            const row =
                Math.floor(index / 2);

            positions[id] = {

                x:
                    column === 0
                        ? 180
                        : 720,

                y:
                    55 +
                    row * rowHeight

            };

        });

        // ------------------------------------------------
        // CREATE SVG
        // ------------------------------------------------

        let svg = `

            <svg
                class="event-graph"
                viewBox="0 0 ${width} ${height}"
                xmlns="http://www.w3.org/2000/svg"
            >
                <defs>
                    <marker
                        id="graph-arrow"
                        viewBox="0 0 10 10"
                        refX="9"
                        refY="5"
                        markerWidth="7"
                        markerHeight="7"
                        orient="auto-start-reverse"
                    >

                        <path
                            d="M 0 0 L 10 5 L 0 10 z"
                            fill="#668cff"
                        />

                    </marker>

                </defs>

        `;

        // ------------------------------------------------
        // DRAW EDGES
        // ------------------------------------------------

        graphRelationships.forEach(r => {

            const from =
                positions[r.from_event];

            const to =
                positions[r.to_event];


            if (!from || !to) {
                return;
            }

            const radius = 40;
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance === 0) {
                return;
            }

            const unitX = dx / distance;
            const unitY = dy / distance;

            const startX = from.x + unitX * radius;
            const startY = from.y + unitY * radius;
            const endX = to.x - unitX * (radius + 8);
            const endY = to.y - unitY * (radius + 8);

            svg += `
                <line
                    class="graph-edge"
                    x1="${startX}"
                    y1="${startY}"
                    x2="${endX}"
                    y2="${endY}"
                    marker-end="url(#graph-arrow)"
                />
            `;

        });

        // ------------------------------------------------
        // DRAW NODES
        // ------------------------------------------------

        nodeIds.forEach(id => {

            const position =
                positions[id];

            const event = eventMap[id];

            const application =
                event?.application || "Unknown";

            const displayApplication =
                application.length > 14
                    ? application.slice(0, 12) + "…"
                    : application;

            const appWords = application.split(/\s+/);
            const appLines = [];
            let currentLine = "";

            appWords.forEach(word => {
                const candidate = currentLine
                    ? `${currentLine} ${word}`
                    : word;

                if (candidate.length > 11 && currentLine) {
                    appLines.push(currentLine);
                    currentLine = word;
                } else {
                    currentLine = candidate;
                }
            });

            if (currentLine) {
                appLines.push(currentLine);
            }

            svg += `

                <g
                    class="graph-node"
                    onclick="showTrace(${id})"
                >

                    <circle
                        cx="${position.x}"
                        cy="${position.y}"
                        r="38"
                    />

                    <text
                        x="${position.x}"
                        y="${position.y - 5}"
                        text-anchor="middle"
                        class="graph-event-id"
                    >
                        #${id}
                    </text>

                    <text
                        x="${position.x}"
                        y="${position.y + 15 - (appLines.length - 1) * 6}"
                        text-anchor="middle"
                        class="graph-app"
                    >

                        ${appLines.map((line, i) => `
                            <tspan
                                x="${position.x}"
                                dy="${i === 0 ? 0 : 13}"
                            >${escapeHtml(
                                line.length > 12
                                    ? line.slice(0, 11) + "…"
                                    : line
                            )}</tspan>
                        `).join("")}

                    </text>

                </g>

            `;

        });


        svg += `</svg>`;


        // ------------------------------------------------
        // DISPLAY
        // ------------------------------------------------

        container.innerHTML = `

            <div class="graph-header">

                <div>

                    <div class="graph-title">
                        Event Flow
                    </div>

                    <div class="graph-subtitle">
                        ${nodeIds.length}
                        events ·
                        ${graphRelationships.length}
                        relationships
                    </div>

                </div>

                <div class="graph-hint">
                    Click a node to Trace
                </div>

            </div>

            <div class="graph-wrapper">

                ${svg}

            </div>

        `;

    }

    catch (error) {

        console.error(
            "Event graph error:",
            error
        );


        container.innerHTML = `

            <div class="empty-state">

                Unable to load event graph.

                <br><br>

                <small>
                    ${escapeHtml(error.message ?? "An unexpected error occurred.")}
                </small>

            </div>

        `;

    }

}

function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


// ============================================================
// BACKWARD TRACE
// ============================================================

async function showTrace(eventId) {

    const numericEventId = Number(eventId);

    if (
        eventId === null ||
        eventId === undefined ||
        String(eventId).trim() === "" ||
        !Number.isInteger(numericEventId) ||
        numericEventId <= 0
    ) {
        console.warn("Invalid event ID:", eventId);
        return;
    }

    try {

        const response =
            await fetch(`/api/trace/${numericEventId}`);

        if (!response.ok) {
            throw new Error(
                `Trace API returned ${response.status}`
            );
        }

        const data =
            await response.json();

        const panel =
            document.getElementById("trace-panel");

        if (!panel) {
            return;
        }

        panel.style.display = "block";

        panel.innerHTML = `

            <div class="trace-header">

                <div>
                    <div class="trace-title">
                        Backward Trace
                    </div>

                    <div class="trace-subtitle">
                        Event #${numericEventId}
                        · Reconstructing surrounding activity
                    </div>
                </div>

                <button
                    class="trace-close"
                    onclick="closeTrace()"
                >
                    ×
                </button>

            </div>


            <div class="trace-flow">


                <div class="trace-section">

                    <div class="trace-section-title">
                        Before
                    </div>

                    <div class="trace-description">
                        Events leading up to the selected activity
                    </div>

                    ${renderTraceEvents(data.before)}

                </div>


                <div class="trace-target">

                    <div class="trace-section-title">
                        Target Event
                    </div>

                    <div class="trace-description">
                        Selected event being investigated
                    </div>

                    ${renderTraceEvent(data.target)}

                </div>


                <div class="trace-section">

                    <div class="trace-section-title">
                        After
                    </div>

                    <div class="trace-description">
                        Events immediately following the selected activity
                    </div>

                    ${renderTraceEvents(data.after)}

                </div>


            </div>

        `;

        panel.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

    catch (error) {

        console.error(
            "Trace error:",
            error
        );

    }

}

function closeTrace() {

    const panel =
        document.getElementById("trace-panel");

    if (!panel) {
        return;
    }

    panel.style.display = "none";

    panel.innerHTML = "";

}

// ============================================================
// TRACE RENDERING
// ============================================================

function renderTraceEvents(events) {

    if (!events || events.length === 0) {

        return `
            <div class="trace-context">
                No events found.
            </div>
        `;

    }

    return events
        .map(event => renderTraceEvent(event))
        .join("");

}




function renderTraceEvent(event) {

    const date = event.timestamp
        ? new Date(event.timestamp)
        : null;

    const formattedTime = date && !isNaN(date.getTime())
        ? date.toLocaleString("en-IN", {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            hour12: true
        })
        : "Time unavailable";

    const application = escapeHtml(
        event.application || "Unknown application"
    );

    const context = escapeHtml(
        event.context || "No context available"
    );

    const rawEventId = event.id;
    const numericEventId = Number(rawEventId);

    const hasValidEventId =
        rawEventId !== null &&
        rawEventId !== undefined &&
        String(rawEventId).trim() !== "" &&
        Number.isInteger(numericEventId) &&
        numericEventId > 0;

    const eventId = escapeHtml(
        hasValidEventId ? numericEventId : "N/A"
    );

    const sessionId = escapeHtml(
        event.session_id ?? "N/A"
    );

    return `
        <div class="trace-event">

            <div class="trace-event-header">

                <div class="trace-app">
                    ${application}
                </div>

                <span class="trace-event-id">
                    Event #${eventId}
                </span>

            </div>

            <div class="trace-time">
                ${escapeHtml(formattedTime)}
            </div>

            <div class="trace-context">
                ${context}
            </div>

            <div class="trace-event-footer">

                <span class="trace-session">
                    Session ${sessionId}
                </span>

                <button
                    class="trace-button"
                    ${hasValidEventId
                        ? `onclick="showTrace(${numericEventId})"`
                        : "disabled"}
                >
                    Trace Event →
                </button>

            </div>

        </div>
    `;
}


// ============================================================
// ASK RETRACE
// ============================================================


async function runQuery() {

    const input =
        document.getElementById("query-input");

    const result =
        document.getElementById("query-result");

    const query =
        input.value.trim();

    if (!query) {

        result.style.display = "block";

        result.innerHTML = `
            <div class="empty-state">
                Enter a question first.
            </div>
        `;

        return;
    }

    result.style.display = "block";

    result.innerHTML = `
        <div class="loading">
            Retrace is searching your history...
        </div>
    `;

    try {

        const naturalResponse =
            await fetch(
                `/api/query/natural?query=${encodeURIComponent(query)}`
            );

        const natural =
            await naturalResponse.json();

        if (!naturalResponse.ok) {

            result.innerHTML = `
                <div class="empty-state">
                    ${escapeHtml(natural.error || "I could not understand that query.")}
                </div>
            `;

            return;
        }

        const queryType =
            natural.query_type;

        const value =
            natural.value;

        let url =
            `/api/query?type=${encodeURIComponent(queryType)}`;

        if (value !== "" && value !== null && value !== undefined) {

            url +=
                `&value=${encodeURIComponent(value)}`;

        }

        // Forward specific date
        if (natural.date) {

            url +=
                `&date=${encodeURIComponent(natural.date)}`;

        }

        const response =
            await fetch(url);

        const data =
            await response.json();

        if (!response.ok) {

            result.innerHTML = `
                <div class="empty-state">
                    ${escapeHtml(data.error || "Query failed.")}
                </div>
            `;

            return;
        }

        renderQueryResult(
            queryType,
            data,
            result
        );

    }

    catch (error) {

        console.error(
            "Query error:",
            error
        );

        result.innerHTML = `
            <div class="empty-state">
                Something went wrong while searching.
            </div>
        `;
    }
}



// ============================================================
// QUERY RESULT
// ============================================================


function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, function (char) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[char];
    });
}

function formatUsageDuration(seconds) {
    const totalSeconds = Math.max(
        0,
        Math.floor(Number(seconds) || 0)
    );

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const remainingSeconds = totalSeconds % 60;

    if (hours > 0) {
        return remainingSeconds > 0
            ? `${hours} hr ${minutes} min ${remainingSeconds} sec`
            : minutes > 0
                ? `${hours} hr ${minutes} min`
                : `${hours} hr`;
    }

    if (minutes > 0) {
        return remainingSeconds > 0
            ? `${minutes} min ${remainingSeconds} sec`
            : `${minutes} min`;
    }

    return `${remainingSeconds} sec`;
}


function renderApplicationPage() {

    const results = currentApplicationResults;
    const container = currentApplicationContainer;

    if (!container || !results.length) return;

    const totalResults = results.length;

    const totalPages = Math.ceil(
        totalResults / APPLICATION_PAGE_SIZE
    );

    applicationResultsPage = Math.min(
        Math.max(1, applicationResultsPage),
        totalPages
    );

    const startIndex =
        (applicationResultsPage - 1) * APPLICATION_PAGE_SIZE;

    const endIndex = Math.min(
        startIndex + APPLICATION_PAGE_SIZE,
        totalResults
    );

    const pageResults = results.slice(
        startIndex,
        endIndex
    );

    container.innerHTML = `
        <div class="query-result-title">
            Application Activity
        </div>

        <div class="query-result-description">
            Found <strong>${totalResults}</strong> events for
            <strong>${escapeHTML(currentApplicationName)}</strong>.
        </div>

        <div class="application-pagination-info">
            Showing ${startIndex + 1}–${endIndex} of ${totalResults} events
        </div>

        <div class="recent-activity-list">
            ${renderTraceEvents(pageResults)}
        </div>

        <div class="application-pagination">

            <button
                class="pagination-button"
                onclick="changeApplicationPage(-1)"
                ${applicationResultsPage === 1 ? "disabled" : ""}
            >
                ← Previous
            </button>

            <span class="pagination-page">
                Page ${applicationResultsPage} of ${totalPages}
            </span>

            <button
                class="pagination-button"
                onclick="changeApplicationPage(1)"
                ${applicationResultsPage === totalPages ? "disabled" : ""}
            >
                Next →
            </button>

        </div>
    `;
}


function changeApplicationPage(direction) {

    const totalPages = Math.ceil(
        currentApplicationResults.length / APPLICATION_PAGE_SIZE
    );

    const nextPage = applicationResultsPage + direction;

    if (nextPage < 1 || nextPage > totalPages) return;

    applicationResultsPage = nextPage;

    renderApplicationPage();
}


function renderQueryResult(
    queryType,
    data,
    container
) {
    // Single-event results: latest / earliest
    if (
        (queryType === "latest" || queryType === "earliest") &&
        data.result
    ) {
        container.innerHTML = `
            <div class="query-result-title">
                ${formatQueryType(queryType)}
            </div>
            <div class="recent-activity-list">
                ${renderTraceEvents([data.result])}
            </div>
        `;
        return;
    }

    // Empty latest / earliest result
    if (
        (queryType === "latest" || queryType === "earliest") &&
        !data.result
    ) {
        container.innerHTML = `
            <div class="query-result-title">
                ${formatQueryType(queryType)}
            </div>
            <div class="empty-state">
                No activity has been recorded yet.
            </div>
        `;
        return;
    }

    const formattedQueryDate = data.date
        ? new Date(data.date + "T00:00:00").toLocaleDateString(
            "en-IN",
            {
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        )
        : null;

    let queryTitle = formatQueryType(queryType);

    if (queryType === "date" && formattedQueryDate) {
        queryTitle = `Activity on ${formattedQueryDate}`;
    }

    if (queryType === "application_date" && formattedQueryDate) {
        queryTitle = `${data.value || "Application"} Activity on ${formattedQueryDate}`;
    }

    container.innerHTML = `
        <div class="query-result-title">
            ${escapeHTML(queryTitle)}
        </div>
    `;

    // Trace / context result
    if (
        data.before &&
        data.target &&
        data.after
    ) {

        container.innerHTML += `

            <div class="trace-section">

                <div class="trace-section-title">
                    Before
                </div>

                ${renderTraceEvents(data.before)}

            </div>

            <div class="trace-target">

                <div class="trace-section-title">
                    Target Event
                </div>

                ${renderTraceEvent(data.target)}

            </div>

            <div class="trace-section">

                <div class="trace-section-title">
                    After
                </div>

                ${renderTraceEvents(data.after)}

            </div>

        `;

        return;
    }
        // Application activity results
    if (
        queryType === "application" ||
        queryType === "application_today" ||
        queryType === "application_yesterday" ||
        queryType === "application_date"
    ) {

        if (data.results && data.results.length > 0) {

            currentApplicationResults = data.results;
            currentApplicationContainer = container;
            currentApplicationName = data.value || "Application";

            applicationResultsPage = 1;

            renderApplicationPage();

        } else {

            container.innerHTML += `
                <div class="empty-state">
                    No recorded activity found for this application.
                </div>
            `;
        }

        return;
    }

    // Yesterday's activity results
    if (queryType === "yesterday") {

        if (data.results && data.results.length > 0) {


            container.innerHTML += `
                <div class="query-result-description">
                    Found ${data.count ?? data.results.length}
                    events from yesterday.
                </div>

                <div class="recent-activity-list">
                    ${renderTraceEvents(data.results)}
                </div>
            `;

        } else {

            container.innerHTML += `
                <div class="empty-state">
                    <div style="font-weight: 600; margin-bottom: 6px;">
                        No activity recorded yesterday
                    </div>
                    <div>
                        Retrace couldn't find any recorded activity
                        from yesterday.
                    </div>
                </div>
            `;
        }

        return;
    }

    // Specific-date activity results
    if (queryType === "date") {

        const formattedDate = data.date
            ? new Date(data.date + "T00:00:00").toLocaleDateString(
                "en-IN",
                {
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                }
            )
            : "the selected date";

        if (data.results && data.results.length > 0) {

            container.innerHTML += `
                <div class="query-result-description">
                    Found ${data.count ?? data.results.length}
                    events on ${escapeHTML(formattedDate)}.
                </div>

                <div class="recent-activity-list">
                    ${renderTraceEvents(data.results)}
                </div>
            `;

        } else {

            container.innerHTML += `
                <div class="empty-state">
                    No activity was recorded on ${escapeHTML(formattedDate)}.
                </div>
            `;
        }

        return;
    }

    // Recent activity results
    if (
        queryType === "recent" &&
        data.results &&
        data.results.length > 0
    ) {
        container.innerHTML += `
            <div class="recent-activity-list">
                ${data.results.map(event => {
            const time = event.timestamp
                ? new Date(event.timestamp).toLocaleString([], {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                })
                : "Time unavailable";

            const application = escapeHTML(
                event.application || "Unknown application"
            );

            const context = escapeHTML(
                event.context || "No context available"
            );

            const activityType = escapeHTML(
                (event.activity_type || "activity")
                    .replaceAll("_", " ")
            );

            return `
                        <div class="query-friendly-result">
                            <div class="query-result-main">
                                <div class="query-result-icon">🟢</div>
                                <div>
                                    <div class="query-result-application">
                                        ${application}
                                    </div>
                                    <div class="query-result-time">
                                        ${time}
                                    </div>
                                </div>
                            </div>
                            <div class="query-result-description">
                                <strong>Activity:</strong> ${activityType}
                                <br>
                                <strong>Context:</strong> ${context}
                                <br>
                                <strong>Event ID:</strong> ${escapeHTML(event.id ?? "N/A")}
                            </div>
                        </div>
                    `;
        }).join("")}
            </div>
        `;

        return;
    }

    // Direct array result
    if (Array.isArray(data)) {

        container.innerHTML +=
            renderTraceEvents(data);

        return;
    }

    // Before / after event results
    if (
        (queryType === "before" || queryType === "after") &&
        Array.isArray(data.results)
    ) {
        if (data.results.length > 0) {
            container.innerHTML += `
            <div class="query-result-description">
                Found ${data.count ?? data.results.length} events
                ${queryType === "before" ? "before" : "after"}
                event ${escapeHTML(data.value ?? "")}.
            </div>
            <div class="recent-activity-list">
                ${renderTraceEvents(data.results)}
            </div>
        `;
        } else {
            container.innerHTML += `
            <div class="empty-state">
                No matching events found.
            </div>
        `;
        }

        return;
    }
    // Events object
    if (data.events) {

        container.innerHTML +=
            renderTraceEvents(data.events);

        return;
    }

    // Session results
    if (queryType === "session") {
        if (data.results && data.results.length > 0) {
            container.innerHTML += `
                <div class="recent-activity-list">
                    <div class="query-result-description">
                        Found ${data.count ?? data.results.length}
                        events in session ${escapeHTML(data.value ?? "")}.
                    </div>
                    ${renderTraceEvents(data.results)}
                </div>
            `;
        } else {
            container.innerHTML += `
                <div class="empty-state">
                    <div style="font-size: 28px; margin-bottom: 10px;">🔍</div>
                    <div style="font-weight: 600; margin-bottom: 6px;">
                        No events found
                    </div>
                    <div>
                        No recorded activity was found for this session.
                    </div>
                </div>
            `;
        }

        return;
    }

    // Before/After application result
    if (
        data.results &&
        data.results.length > 0 &&
        (
            queryType === "before_application" ||
            queryType === "after_application"
        )
    ) {

        const event = data.results[0];

        const time = new Date(
            event.timestamp
        ).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        const direction =
            queryType === "before_application"
                ? "before"
                : "after";

        const targetApplication =
            data.value || "the application";

        container.innerHTML += `

            <div class="query-friendly-result">

                <div class="query-result-main">

                    <div class="query-result-icon">
                        🟢
                    </div>

                    <div>

                        <div class="query-result-application">
                            ${escapeHtml(event.application ?? "Unknown")}
                        </div>

                        <div class="query-result-time">
                            ${time}
                        </div>

                    </div>

                </div>

                <div class="query-result-description">

                    You were using
                    <strong>${escapeHtml(event.application ?? "Unknown")}</strong>
                    immediately ${escapeHtml(direction)}
                    opening
                    <strong>${escapeHtml(targetApplication ?? "Unknown")}</strong>.

                </div>

            </div>

        `;

        return;
    }

    // Most-used application results
    if (queryType === "most_used") {

        if (data.results && data.results.length > 0) {

            const topApplication = data.results[0];
            const otherApplications = data.results.slice(1, 4);

            container.innerHTML += `
                <div class="most-used-highlight">

                    <div class="most-used-highlight-header">
                        <span class="most-used-label">MOST USED</span>
                        <span class="most-used-trophy">🏆</span>
                    </div>

                    <div class="most-used-winner">
                        ${escapeHTML(topApplication.application)}
                    </div>

                    <div class="most-used-winner-duration">
                        ${formatUsageDuration(topApplication.duration)}
                    </div>

                    <div class="most-used-caption">
                        Highest recorded application usage
                    </div>

                </div>

                <div class="most-used-others">

                    <div class="query-result-description">
                        <strong>Other frequently used applications</strong>
                    </div>

                    <div class="most-used-list">

                        ${otherApplications.map((app, index) => `
                            <div class="most-used-item">

                                <span class="most-used-rank">
                                    ${index + 2}
                                </span>

                                <span class="most-used-name">
                                    ${escapeHTML(app.application)}
                                </span>

                                <span class="most-used-duration">
                                    ${formatUsageDuration(app.duration)}
                                </span>

                            </div>
                        `).join("")}

                    </div>

                </div>
            `;

        } else {

            container.innerHTML += `
                <div class="empty-state">
                    No application usage data is available.
                </div>
            `;
        }

        return;
    }
    // No results
    if (
        data.results &&
        data.results.length === 0
    ) {

        container.innerHTML += `

            <div class="empty-state">

                <div style="font-size: 28px; margin-bottom: 10px;">
                    🔍
                </div>

                <div style="font-weight: 600; margin-bottom: 6px;">
                    No activity found
                </div>

                <div>
                    Retrace couldn't find any matching activity
                    for this query.
                </div>

            </div>

        `;

        return;
    }



    // Fallback
    container.innerHTML += `

        <div class="trace-context">

            ${escapeHtml(JSON.stringify(data))}

        </div>

    `;

}

// ============================================================
// SIDEBAR NAVIGATION
// ============================================================

const viewConfig = {
    overview: {
        title: "Overview",
        show: [
            "usage",
            "timeline",
            "sessions",
            "signals",
            "relationships-container",
            "query-input"
        ]
    },

    timeline: {
        title: "Timeline",
        show: [
            "timeline-page"
        ]
    },

    sessions: {
        title: "Sessions",
        show: [
            "sessions"
        ]
    },

    analytics: {
        title: "Analytics",
        show: [
            "usage"
        ]
    },

    patterns: {
        title: "Patterns",
        show: [
            "signals"
        ]
    },

    query: {
        title: "Ask Retrace",
        show: [
            "query-input"
        ]
    },

    graph: {
        title: "Event Graph",
        show: [
            "relationships-container"
        ]
    },

    settings: {
        title: "Settings",
        show: []
    }
};


// ============================================================
// FIND PANEL CONTAINING AN ELEMENT
// ============================================================

function getPanel(elementId) {

    const element =
        document.getElementById(elementId);

    if (!element) {
        return null;
    }

    return element.closest(
        ".panel, .dashboard-panel, .section"
    );

}

// ============================================================
// HIDE ALL CONTENT PANELS
// ============================================================

function hideAllPanels() {

    const ids = [
        "usage",
        "timeline",
        "timeline-page",
        "sessions",
        "signals",
        "relationships-container",
        "query-input",
        "trace-panel"
    ];

    ids.forEach(id => {

        const panel = getPanel(id);

        if (panel) {
            panel.style.display = "none";
        }

    });

}

async function loadFullTimeline() {

    const container =
        document.getElementById("timeline-events");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            Loading timeline...
        </div>
    `;

    try {

        const response =
            await fetch("/api/timeline");

        if (!response.ok) {
            throw new Error(
                `Timeline API returned ${response.status}`
            );
        }

        const events =
            await response.json();

        window.retraceTimeline =
            events || [];

        renderFullTimeline(
            window.retraceTimeline
        );

    }

    catch (error) {

        console.error(
            "Timeline error:",
            error
        );

        container.innerHTML = `
            <div class="empty-state">
                Unable to load timeline.

                <br><br>

                <small>
                    ${escapeHtml(error.message)}
                </small>

            </div>
        `;

    }

}

function renderFullTimeline(events) {

    const container =
        document.getElementById("timeline-events");

    if (!container) {
        return;
    }

    if (!events || events.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No events recorded.
            </div>
        `;

        return;
    }

    container.innerHTML =
        events.map(event => `

            <div
                class="timeline-event"
                ${event.id !== null &&
                event.id !== undefined &&
                String(event.id).trim() !== "" &&
                Number.isInteger(Number(event.id)) &&
                Number(event.id) > 0
                    ? `onclick="showTrace(${Number(event.id)})"`
                    : ""}
            >

                <div class="timeline-dot"></div>

                <div class="timeline-content">

                    <div class="timeline-time">
                        ${escapeHtml(event.timestamp)}
                    </div>

                    <div class="timeline-app">
                        ${escapeHtml(
            event.application ||
            "Unknown"
        )}
                    </div>

                    <div class="timeline-type">
                        ${escapeHtml(
            event.activity_type ||
            "activity"
        )}
                    </div>

                    <div class="timeline-context">
                        ${escapeHtml(
            event.context ||
            "No context"
        )}
                    </div>

                </div>

                <div class="timeline-event-id">
                    #${escapeHtml(event.id ?? "N/A")}
                </div>

            </div>

        `).join("");

}


function initializeTimelineFilter() {

    const filter =
        document.getElementById(
            "timeline-filter"
        );

    if (!filter) {
        return;
    }

    filter.onchange = () => {

        const selected =
            filter.value;

        const events =
            window.retraceTimeline || [];

        if (selected === "all") {

            renderFullTimeline(events);

            return;
        }

        const filtered =
            events.filter(
                event =>
                    event.application === selected
            );

        renderFullTimeline(filtered);

    };

}

// ============================================================
// SHOW SELECTED VIEW
// ============================================================

function showView(viewName) {

    const config =
        viewConfig[viewName];

    if (!config) {
        return;
    }

    // Hide existing panels

    hideAllPanels();

    // Show requested panels

    config.show.forEach(id => {

        const panel =
            getPanel(id);

        if (panel) {
            panel.style.display = "";
        }

    });


    // Update page title

    const title = document.getElementById("page-title");
    if (title) title.textContent = config.title;


    // Update sidebar active state

    document
        .querySelectorAll(".nav-item")
        .forEach(item => {

            item.classList.remove("active");

        });


    const activeItem =
        document.querySelector(
            `[data-view="${viewName}"]`
        );

    if (activeItem) {
        activeItem.classList.add("active");
    }


    // Load Event Graph

    if (viewName === "graph") {
        loadRelationships();
    }


    // Load full Timeline

    if (viewName === "timeline") {
        loadFullTimeline();
        initializeTimelineFilter();
    }


    // Scroll to top

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}

// ============================================================
// INITIALIZE SIDEBAR
// ============================================================

function initializeNavigation() {
    const queryInput = document.getElementById("query-input");
    if (queryInput && !queryInput.dataset.keyboardReady) {
        queryInput.dataset.keyboardReady = "true";
        queryInput.addEventListener("keydown", event => {
            if (event.key === "Enter") runQuery();
        });
    }
    document.querySelectorAll(".brand[data-view]").forEach(item => {
        item.addEventListener("click", event => { event.preventDefault(); showView("overview"); });
    });

    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );


    navItems.forEach(item => {

        item.addEventListener(
            "click",
            event => {

                event.preventDefault();

                const view =
                    item.dataset.view;

                if (view) {
                    showView(view);
                }

            }
        );

    });


    // Start on Overview

    showView("overview");

}


// ============================================================
// START NAVIGATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeNavigation();

    }
);

function formatQueryType(type) {

    return type
        .replaceAll("_", " ")
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );

}

function resetGraphRange() {
    const startInput = document.getElementById("graph-start-event");
    const endInput = document.getElementById("graph-end-event");

    if (startInput) startInput.value = "";
    if (endInput) endInput.value = "";

    loadRelationships();
}


async function updateCollectorStatus() {
    const statusValue = document.getElementById("collector-status-value");
    const statusMessage = document.getElementById("collector-status-message");
    const startButton = document.getElementById("collector-start-btn");
    const stopButton = document.getElementById("collector-stop-btn");

    try {
        const response = await fetch("/api/collector/status");

        if (!response.ok) {
            throw new Error("Failed to fetch collector status");
        }

        const data = await response.json();
        const status = data.status;

        const isRunning = status === "running";
        const isStopping = status === "stopping";
        const isStopped = status === "stopped";

        if (statusValue) {
            const statusText = isRunning
                ? "Running"
                : isStopping
                    ? "Stopping"
                    : isStopped
                        ? "Stopped"
                        : "Unknown";

            statusValue.innerHTML = `
                ${statusText}
                <span class="active-indicator"></span>
            `;
        }

        if (statusMessage) {
            statusMessage.textContent = isRunning
                ? "Local activity collector is running"
                : isStopping
                    ? "Collector is shutting down..."
                    : isStopped
                        ? "Activity collection is stopped"
                        : "Collector status is unavailable";
        }

        if (startButton) {
            startButton.disabled = isRunning || isStopping;
        }

        if (stopButton) {
            stopButton.disabled = isStopped || isStopping;
        }

    } catch (error) {
        console.error("Collector status error:", error);

        if (statusMessage) {
            statusMessage.textContent =
                "Unable to connect to the collector API";
        }
    }
}


async function updateSidebarCollectorStatus() {
    try {
        const response = await fetch("/api/collector/status");

        if (!response.ok) {
            throw new Error("Unable to fetch collector status");
        }

        const data = await response.json();

        const title = document.getElementById("sidebar-status-title");
        const description = document.getElementById("sidebar-status-description");
        const pulse = document.getElementById("sidebar-status-pulse");

        if (!title || !description || !pulse) return;

        const isRunning = data.status === "running";
        const isStopping = data.status === "stopping";

        title.textContent = isRunning
            ? "Collector running"
            : isStopping
                ? "Collector stopping"
                : "Collector stopped";

        description.textContent = isRunning
            ? "Capturing desktop activity"
            : isStopping
                ? "Shutting down activity collection"
                : "Activity collection is stopped";

        pulse.classList.toggle("active", isRunning);
        pulse.classList.toggle("inactive", !isRunning);

    } catch (error) {
        console.error("Sidebar collector status error:", error);
    }
}


async function initializeCollectorControls() {
    const startButton = document.getElementById("collector-start-btn");
    const stopButton = document.getElementById("collector-stop-btn");

    if (!startButton || !stopButton) {
        console.error("Collector control buttons were not found.");
        return;
    }

    startButton.addEventListener("click", async () => {
        startButton.disabled = true;
        stopButton.disabled = true;
        startButton.textContent = "Starting...";

        try {
            const response = await fetch("/api/collector/start", {
                method: "POST"
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Could not start collection"
                );
            }

            await loadDashboard();

        } catch (error) {
            console.error("Collector start error:", error);

            alert(
                "Could not start collection. Check that the Retrace server is running."
            );

        } finally {
            startButton.textContent = "Start Tracking";

            await updateCollectorStatus();
            await updateSidebarCollectorStatus();
        }
    });


    stopButton.addEventListener("click", async () => {
        startButton.disabled = true;
        stopButton.disabled = true;
        stopButton.textContent = "Stopping...";

        try {
            const response = await fetch("/api/collector/stop", {
                method: "POST"
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Could not stop collection"
                );
            }

            await loadDashboard();

        } catch (error) {
            console.error("Collector stop error:", error);

            alert(
                "Could not stop collection. Check that the Retrace server is running."
            );

        } finally {
            stopButton.textContent = "Stop Tracking";

            await updateCollectorStatus();
            await updateSidebarCollectorStatus();
        }
    });


    await updateCollectorStatus();
    await updateSidebarCollectorStatus();
}