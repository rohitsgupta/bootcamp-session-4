# Slalom Capabilities Management API

<p align="center">
  <img src="./.images/byte-teacher.png" alt="Byte Teacher" width="200" />
</p>

A FastAPI application that enables Slalom consultants to register their capabilities and manage consulting expertise across the organization.

## Features

- View all available consulting capabilities
- Register consultant expertise and availability
- Track skill levels and certifications
- Manage capability capacity and team assignments
- Persist capabilities and assignments in a local SQLite database
- Filter/search capabilities and use versioned API routes under `/v1`

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

   Optional: override the default database location:

   ```
   CAPABILITIES_DB_PATH=/path/to/capabilities.db python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc
   - Capabilities Dashboard: http://localhost:8000/

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/capabilities`                                                   | Get all capabilities with details and current consultant assignments |
| POST   | `/capabilities/{capability_name}/register?email=consultant@slalom.com` | Register consultant for a capability                     |
| DELETE | `/capabilities/{capability_name}/unregister?email=consultant@slalom.com` | Unregister consultant from a capability              |

Versioned aliases are also available:

- `GET /v1/capabilities`
- `POST /v1/capabilities/{capability_name}/register`
- `DELETE /v1/capabilities/{capability_name}/unregister`

Capability retrieval supports optional query params:

- `limit` and `offset` for pagination (for example `/capabilities?limit=5&offset=0`)
- `practice_area` for exact filtering (for example `/capabilities?practice_area=Technology`)
- `search` for name/description matching (for example `/capabilities?search=cloud`)

## Data Model

The application uses a consulting-focused data model:

1. **Capabilities** - Uses capability name as identifier:
   - Description of the consulting capability
   - Skill levels (Emerging, Proficient, Advanced, Expert)
   - Practice area (Strategy, Technology, Operations)
   - Industry verticals served
   - Required certifications
   - List of consultant emails registered
   - Available capacity (hours per week)
   - Geographic location preferences

2. **Consultants** - Uses email as identifier:
   - Name
   - Practice area
   - Skill level
   - Certifications
   - Availability

Data is now persisted in SQLite for local development. On first startup, the app creates tables and seeds default capabilities if the database is empty.

## Future Enhancements

This exercise will guide you through implementing:
- Capability maturity assessments
- Intelligent team matching algorithms  
- Analytics dashboards for practice leads
- Integration with project management systems
- Advanced search and filtering capabilities
