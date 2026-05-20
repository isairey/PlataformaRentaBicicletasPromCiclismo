# Bike Network System

## Project Description

System for bike rental management and cycling activity promotion. Includes event and route scheduling, an interactive map with Leaflet, and bike inventory control.

## Team

| Role          | Name                |
| ------------- | ------------------- |
| Product Owner | Carlos Alberto Mazo |
| Scrum Master  | Patricia Arango     |
| Developer 1   | Jehison David Cifuentes    |
| Developer 3   | Miguel Vasquez      |
| Developer 4   | Jhonnathan Ocampo   |
| QA            | Oswaldo Alzate      |

## Deliverables

### 1. Functional Requirements

| ID    | Requirement                                                                 | Module           |
| ----- | --------------------------------------------------------------------------- | ---------------- |
| RF-01 | The system must allow a user to register with name, email and password      | `authentication` |
| RF-02 | The system must allow a user to authenticate with email and password        | `authentication` |
| RF-03 | The system must allow a user to log out and invalidate the token            | `authentication` |
| RF-04 | The system must allow adding a bike with ID, brand, type, color and status  | `bike-crud`      |
| RF-05 | The system must allow listing all bikes                                     | `bike-crud`      |
| RF-06 | The system must allow editing a bike's information                          | `bike-crud`      |
| RF-07 | The system must allow deleting a bike that is not currently rented          | `bike-crud`      |
| RF-08 | The system must allow an authenticated user to rent an available bike       | `rental`         |
| RF-09 | The system must mark a bike as unavailable when it is rented                | `rental`         |
| RF-10 | The system must allow returning a bike and mark it as available             | `rental`         |
| RF-11 | The system must display the rented bike on an interactive map using Leaflet | `map`            |
| RF-12 | The system must allow consulting scheduled cycling events                   | `events`         |
| RF-13 | The system must allow consulting available cycling routes                   | `events`         |
| RF-14 | The system must allow consulting scheduled competitions                     | `events`         |

### 2. NRF vs QoS Mapping

| QoS Attribute        | Description                                       |
| -------------------- | ------------------------------------------------- |
| **Performance**      | Response time and throughput                      |
| **Availability**     | System uptime and fault tolerance                 |
| **Security**         | Authentication, authorization and data protection |
| **Scalability**      | Ability to handle growing load                    |
| **Maintainability**  | Ease of updating and testing the codebase         |
| **Usability**        | User experience and error handling                |
| **Reliability**      | Consistency and data integrity                    |
| **Interoperability** | Ability to integrate with other systems           |
| **Compatibility**    | Support across browsers and platforms             |

| RNF    | Requirement                                                                     | QoS Attribute    |
| ------ | ------------------------------------------------------------------------------- | ---------------- |
| RNF-01 | The system must respond to any request in less than 2 seconds under normal load | Performance      |
| RNF-02 | The system must be available 95% of the time                                    | Availability     |
| RNF-03 | All passwords must be stored using a hashing algorithm (bcrypt)                 | Security         |
| RNF-04 | All API endpoints except public ones must require JWT authentication            | Security         |
| RNF-05 | The system must support up to 50 concurrent users                               | Scalability      |
| RNF-06 | The interactive map must load in less than 3 seconds                            | Performance      |
| RNF-07 | The system must run on modern browsers (Chrome, Firefox, Edge)                  | Compatibility    |
| RNF-08 | The API must follow REST conventions and return JSON responses                  | Interoperability |
| RNF-09 | The codebase must have at least 70% test coverage                               | Maintainability  |
| RNF-10 | The system must provide meaningful error messages to the user                   | Usability        |
| RNF-11 | The databases must support rollback in case of failed transactions              | Reliability      |
| RNF-12 | The databases must have a migration system                                     | Reliability      |

### 3. Context Diagram

<img width="3288" height="2964" alt="image" src="https://github.com/user-attachments/assets/4c0c877c-65e2-4cd4-8ee4-f1a253c0163d" />

### 4. User Stories

https://github.com/users/camazog1/projects/9

### 5. Component Diagram (Logical and Technical)

<img width="2483" height="1784" alt="Untitled (1)" src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/DiagramComponent.png" />

### 6. Sequence Diagrams

<img width="2483" height="1784" alt="Untitled (1)" src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/sequence_diagrams_user.png" />

<img width="2483" height="1784" alt="Untitled (1)" src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/sequence_diagrams_rent.png" />

<img width="2483" height="1784" alt="Untitled (1)" src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/sequence_diagrams_Map_bikes.png" />

### 7. Deployment Diagram

<img width="2483" height="1784" alt="Untitled (1)" src="https://github.com/user-attachments/assets/35c0a090-4014-45ec-b37f-bc731c54868c" />

## Architecture Decisions

### Architectural Decision: Cloud Infrastructure & Deployment

[docs/Architectural Decision: Cloud Infrastructure & Deployment.md](https://github.com/camazog1/Bike-Network-System/blob/main/docs/Architectural%20Decision%20Cloud%20Infrastructure%20%26%20Deployment.md)

### Architectural Decision: Technology Stack & Development Practices

[docs/Architectural Decision: Technology Stack & Development Practices.md](https://github.com/camazog1/Bike-Network-System/blob/main/docs/Architectural%20Decision%20Technology%20Stack%20%26%20Development%20Practices.md)
