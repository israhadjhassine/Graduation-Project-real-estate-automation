# Analysis of PFE_Documentation_EliteEstate.pdf & Required Updates

This document analyzes the generated academic report [PFE_Documentation_EliteEstate.pdf](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/docs/PFE_Documentation_EliteEstate.pdf) and its source markdown document [PFE_Documentation_EliteEstate.md](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/docs/plans/PFE_Documentation_EliteEstate.md) to identify structural, factual, and terminology updates required to align the report with the actual codebase, standard real estate terminology, and corrected user roles.

---

## 1. Core Discrepancies & Required Fixes

### A. Role Definition Realignment: "Visitor" vs. "Client"
*   **The Issue:** The current documentation treats **Visitor** as a database-level, registered role (part of a "4-role RBAC" system) that possesses advanced features like visit scheduling, Telegram AI interactions, and RAG-based conversations.
*   **The Correction:** 
    *   **Visitor** is strictly an anonymous, unauthenticated public guest state (no database record, no auth, no bot memory).
    *   **Client** is the registered customer role in the database. A Client has a profile, booking rights, AI RAG assistant usage, and Telegram Bot personalization (tracked via `telegram_chat_id`).
*   **Locations to Update:**
    1.  **Section 2.2 (Project Objectives - Row 7 of Table):** Change *"4-role RBAC: Admin, Head Agent, Sub-Agent, Visitor"* to *"4-role RBAC: Admin, Head Agent, Sub-Agent, Client (plus unauthenticated Visitor access)"*.
    2.  **Section 6.1.1 (Role-Based Access Control Table):** Rename the `visitor` role row to `client` and update permissions. Add a separate note for **Visitor (Unauthenticated)**.
    3.  **Section 9.1 (Key User Roles Use Case Table):** Add **Client** as the primary actor for registration, profile management, AI RAG questions, visit booking, and Telegram AI personalization. Strip **Visitor** down to anonymous searching and listing browsing.

---

### B. Database Schema & Models Alignment
*   **The Issue:** The database design section (Section 6.2) contains some legacy column terms or doesn't reflect the removal of redundant boolean flags in the `Property` model in favor of the Many-to-Many `property_features` table.
*   **The Correction:** Ensure the text exactly reflects the normalized PostgreSQL schema defined in [models.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/models.py).
    *   Make sure `Property` lists its normalized columns.
    *   Explicitly show the relationship with the `property_features` (M2M join table) instead of legacy inline fields.

---

### C. Framework & Tech Stack Updates: Nuxt 3 vs. Nuxt 4
*   **The Issue:** The documentation refers to the frontend as **Nuxt 3** throughout sections 1.1, 4.3, 6.1.2, and 6.4.
*   **The Correction:** The frontend `package.json` specifies `"nuxt": "^4.3.1"`. To maintain absolute academic accuracy, all references to **Nuxt 3** must be updated to **Nuxt 4**.
*   **Locations to Update:**
    *   Section 1.1 (Introduction / Executive Summary)
    *   Section 4.3 (Frontend Framework selection justification)
    *   Section 6.1.2 (System Component Table)
    *   Section 6.4 (Frontend Architecture and Views)

---

### D. System & DB Default Alignment
*   **The Issue:** Currently, the database default role for a user (defined in [models.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/models.py) and [schemas.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/schemas.py)) is `"visitor"`.
*   **The Correction:** The default role must be changed to `"client"` to match the frontend registration system.

---

## 2. Table of Specific Document Updates

| Section in MD / PDF | Current Text / Concept | Corrected Text / Concept |
|:---|:---|:---|
| **Section 2.2** | `4-role RBAC: Admin, Head Agent, Sub-Agent, Visitor` | `4-role RBAC: Admin, Head Agent, Sub-Agent, Client` (Visitor is anonymous guest state) |
| **Section 4.3** | `Frontend Framework: Nuxt 3 (Vue.js)` | `Frontend Framework: Nuxt 4 (Vue.js 3)` |
| **Section 6.1.1** | Role `visitor` can browse, search, book visits in RBAC table | Role `client` can browse, search, book visits, interact with Telegram Bot, update profile. Add anonymous `visitor` guest permissions below the table. |
| **Section 6.1.2** | `Nuxt 3 / Vue 3 / TypeScript` in technology table | `Nuxt 4 / Vue 3 / TypeScript` |
| **Section 6.4** | `Frontend built using Nuxt 3` | `Frontend built using Nuxt 4` |
| **Section 9.1** | Actor `Visitor` does browse, search, map, AI questions, Telegram Bot | Actor `Visitor` (Anonymous): Browse, basic filter search, view map.<br>Actor `Client` (Registered): Profile settings, book visits, AI RAG assistant questions, personalized Telegram Bot tool interactions. |

---

## 3. Summary of Code Updates to Align
To match the documentation updates, we will perform the following code updates:
1.  **[models.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/models.py):** Set `User.role` default value to `"client"`.
2.  **[schemas.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/schemas.py):** Set `UserCreate.role` default value to `"client"`.
3.  **[user_repository.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/repositories/user_repository.py):** Change `role != "visitor"` to `role != "client"` inside `get_all_staff()`.
4.  **[auth.ts](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/frontend/app/stores/auth.ts):** Update typescript roles interfaces to support `client` and fallback compatibility for any existing roles.
