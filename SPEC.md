# Nespresso Pod Random Selector - Specification Document

## 1. Project Overview
- **Project Name**: Nespresso Pod Random Selector
- **Type**: Full-stack Web Application
- **Core Functionality**: A web app to randomly select Nespresso pods based on user preferences and track inventory
- **Target Users**: Nespresso machine owners who want help deciding which pod to brew

## 2. Technical Architecture

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Scheduler**: APScheduler for monthly updates

### Frontend
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Mobile-first, responsive design

### Features Breakdown

#### 2.1 Web Scraper
- Scrape all Nespresso pods from official website
- Data fields: name, tasting note, size (ml), type (espresso/double espresso/lungo)
- Auto-update every 1 month

#### 2.2 User Inventory Management
- Add/remove pods with quantities
- Support multiple users
- Each user has their own inventory

#### 2.3 Random Selection Logic
- Filter by pod type (espresso/double/lungo) or no filter
- Exclude pods with quantity = 0
- Random selection from filtered list

#### 2.4 Inventory Tracking
- Decrement quantity by 1 when confirmed
- Auto-remove pods with quantity = 0 from selection

#### 2.5 Internationalization
- Chinese (Simplified) and English support
- Language toggle button

#### 2.6 Branding
- "Powered by XXX" footer banner

## 3. Data Models

### Pod (Master Data)
- id: Integer (Primary Key)
- name: String
- name_en: String
- tasting_note: String
- tasting_note_en: String
- size_ml: Integer
- pod_type: String (espresso/double/lungo/vertino)
- last_updated: DateTime

### User
- id: Integer (Primary Key)
- username: String (Unique)
- created_at: DateTime

### UserInventory
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- pod_id: Integer (Foreign Key)
- quantity: Integer

## 4. API Endpoints

- `GET /api/pods` - Get all master pod data
- `POST /api/inventory` - Add/update inventory item
- `DELETE /api/inventory/<id>` - Remove inventory item
- `GET /api/inventory/<user_id>` - Get user's inventory
- `GET /api/random/<user_id>` - Get random pod based on preference
- `POST /api/confirm` - Confirm selection and decrement quantity
- `GET /api/scrape` - Trigger manual scrape (admin)

## 5. UI Components

1. **Header**: Logo + Language toggle + User selector
2. **Inventory Section**: List of owned pods with edit/delete
3. **Random Selector**: Preference buttons + Random button + Result display
4. **Footer**: Powered by banner

## 6. Acceptance Criteria

1. ✓ Can scrape Nespresso pod data automatically
2. ✓ Can manually add/edit/remove user's pod inventory
3. ✓ Random selection works with type filtering
4. ✓ Quantity decrements on confirmation
5. ✓ Zero-quantity pods excluded from selection
6. ✓ Mobile-friendly responsive design
7. ✓ Full Chinese/English language support
8. ✓ Multi-user support
9. ✓ Footer banner displays correctly
