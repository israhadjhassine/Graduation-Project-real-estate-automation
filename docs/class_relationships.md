# UML Domain Relationships & Multiplicities — Elite Estate

This document details the conceptual relationships, association directions, and multiplicities for the Elite Estate domain model.

---

## 1. User & Access Control Cluster

| Relationship | Association Direction | Multiplicity | Conceptual Rule / Explanation |
| :--- | :--- | :--- | :--- |
| **Agent $\rightarrow$ HeadAgent** | Agent `*` $\rightarrow$ `0..1` HeadAgent | **Many-to-One** | Many Agents report to a single Head Agent who coordinates the team. An Agent reports to at most `1` Head Agent. |
| **User $\rightarrow$ TelegramPairingCode** | User `1` $\rightarrow$ `0..1` TelegramPairingCode | **One-to-Optional-One** | A User can generate at most `1` active Telegram pairing code at a time. The code belongs to exactly `1` User. |
| **Admin $\rightarrow$ User** | Admin `1` $\rightarrow$ `*` User | **One-to-Many** | An Admin manages system access for many Users. |

---

## 2. Property & Content Cluster

| Relationship | Association Direction | Multiplicity | Conceptual Rule / Explanation |
| :--- | :--- | :--- | :--- |
| **Property $\times$ PropertyImage** | Property `1` `*--` `*` PropertyImage | **Composition (1-to-Many)** | A Property contains zero or many images. Because this is **Composition**, a `PropertyImage` cannot exist without its parent `Property` (if the property is deleted, all its images are deleted). |
| **Property $\times$ Feature** | Property `*` `--` `*` Feature | **Many-to-Many** | A Property can have multiple features (e.g., *Pool, Elevator, Garage*), and a single Feature can be linked to multiple different properties. |
| **Client $\rightarrow$ Property** | Client `0..1` $\rightarrow$ `*` Property | **Many-to-Optional-One** | A Client can own many properties listed on the platform. A property can either belong to `1` client or none (if owned directly by the agency). |
| **Agent $\rightarrow$ Property** | Agent `0..1` $\rightarrow$ `*` Property | **Many-to-Optional-One** | An Agent manages many properties. A property has at most `1` assigned managing agent. |

---

## 3. Scheduling & Visit Cluster

| Relationship | Association Direction | Multiplicity | Conceptual Rule / Explanation |
| :--- | :--- | :--- | :--- |
| **Property $\rightarrow$ Visit** | Property `1` $\rightarrow$ `*` Visit | **One-to-Many** | A Property can host many scheduled visits over time. A Visit is for exactly `1` Property. |
| **Client $\rightarrow$ Visit** | Client `1` $\rightarrow$ `*` Visit | **One-to-Many** | A Client schedules many visits. A Visit belongs to exactly `1` Client. |
| **Agent $\rightarrow$ Visit** | Agent `1` $\rightarrow$ `*` Visit | **One-to-Many** | An Agent conducts many visits. A Visit is conducted by exactly `1` Agent. |

---

## 4. Transaction Request & Reporting Cluster

| Relationship | Association Direction | Multiplicity | Conceptual Rule / Explanation |
| :--- | :--- | :--- | :--- |
| **Property $\rightarrow$ TransactionRequest** | Property `1` $\rightarrow$ `*` TransactionRequest | **One-to-Many** | A Property triggers many transaction requests (some approved, some rejected). A request is for exactly `1` Property. |
| **Client $\rightarrow$ TransactionRequest** | Client `1` $\rightarrow$ `*` TransactionRequest | **One-to-Many** | A Client creates many transaction requests. A request is created by exactly `1` Client. |
| **Agent $\rightarrow$ TransactionRequest** | Agent `1` $\rightarrow$ `*` TransactionRequest | **One-to-Many** | An Agent handles many transaction requests. A request is handled by exactly `1` Agent. |
| **Property $\rightarrow$ Report** | Property `1` $\rightarrow$ `*` Report | **One-to-Many** | A Property can generate multiple reports over its transaction lifecycle. A Report is generated for exactly `1` Property. |
| **Agent $\rightarrow$ Report** | Agent `0..1` $\rightarrow$ `*` Report | **Many-to-Optional-One** | An Agent files many reports. A report is filed by at most `1` Agent. |
| **Client $\rightarrow$ Report** | Client `0..1` $\rightarrow$ `*` Report | **Many-to-Optional-One** | A Client participates as the buyer/tenant in many transaction reports. A report tracks at most `1` buyer Client. |
| **Admin $\rightarrow$ Report** | Admin `1` $\rightarrow$ `*` Report | **One-to-Many** | An Admin audits/downloads many reports for system accounting. |
