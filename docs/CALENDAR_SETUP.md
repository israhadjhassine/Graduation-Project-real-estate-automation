# Google Calendar Integration Guide

This guide explains how to set up and manage the two-layer Google Calendar architecture for **Elite Estate**.

---

## Layer 1: Shared Agency Calendar (Current Active Setup)

The **Elite Estate — Visits** calendar is a single, shared calendar used for all property visits. This setup provides centralized visibility for the entire agency team.

### Administrator Setup Steps
1.  **Create the Calendar**: Go to [https://calendar.google.com](https://calendar.google.com). Click **+ Other calendars** → **Create new calendar**. Name it `Elite Estate — Visits`.
2.  **Share with Agents**: Open the calendar settings. Under **Share with specific people**, add each agent's email address and assign them **Make changes to events** permission.
3.  **Configure n8n Workflow**:
    *   Copy the **Calendar ID** (e.g., `xxxxx@group.calendar.google.com`) from the calendar settings.
    *   Open the n8n workflow.
    *   Locate the four Google Calendar nodes: `get_events`, `create_event`, `update_event`, and `delete_event`.
    *   Replace the temporary personal email address in these nodes with the new **Calendar ID**.
4.  **Automatic Sync**: Once set up, all agents added to the shared calendar will see all upcoming bookings appear automatically in their local Google Calendar app on their phone or desktop.

---

## Layer 2: Per-Agent Calendar Routing (Production Ready)

The per-agent routing infrastructure is built into the backend but is not yet activated in the live n8n workflow. This setup allows visits to be booked directly onto an agent's personal calendar.

### Agent Setup Steps (Activation Requirements)
To "connect" their personal calendar, each agent must complete these two steps:

1.  **Elite Estate Profile**: Go to your profile settings on the Elite Estate dashboard. In the **Google Calendar ID** field, enter your personal Gmail address (e.g., `agent.name@gmail.com`) and save.
2.  **Google Calendar Permission**:
    *   Go to [https://calendar.google.com](https://calendar.google.com).
    *   Find your personal calendar under **My calendars**, click the three dots (**⋮**) next to it, and select **Settings and sharing**.
    *   Scroll down to **Share with specific people** and add the **Agency's Main Google account email**.
    *   Set the permission level to **Make changes to events**.

### How it works technically
The infrastructure is ready:
- The `google_calendar_id` exists in the database.
- The `PUT /auth/profile` endpoint allows agents to save their ID.
- The `POST /search/rag` endpoint automatically returns the `agent_calendar_id` for every property found.
- To activate this in production, the n8n calendar nodes only need a small update to read the `agent_calendar_id` dynamically from the RAG search response.

---

## Why the Two-Layer Approach?
- **Immediate Value**: Layer 1 works instantly with zero configuration for agents and provides a unified "Agency Overview" of all visits.
- **Future Proof**: Layer 2 allows the platform to scale into a fully personalized booking system as the agency grows, requiring no further backend code changes.
