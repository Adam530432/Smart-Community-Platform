# Smart Community Platform API Documentation

## Table of Contents
1. [User Management](#user-management)
2. [Bill Management](#bill-management)
3. [Visitor Management](#visitor-management)
4. [Maintenance Management](#maintenance-management)
5. [Announcement Management](#announcement-management)

## General Information

### Response Format
All API responses follow this format:
```json
{
    "code": 200,       // Status code
    "message": "",     // Response message
    "data": {}         // Response data
}
```

### Status Codes
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## User Management

### 1. User Login
- **URL:** `/login`
- **Method:** POST
- **Request Parameters:**
  ```json
  {
    "username": "string",    // Username/Phone number
    "password": "string"     // Password
  }
  ```
- **Success Response:**
  ```json
  {
    "code": 200,
    "message": "Login successful",
    "data": {
      "user_id": 1,
      "name": "John Doe",
      "apartment_number": "6-888",
      "phone_number": "13800138000"
    }
  }
  ```
- **Error Response:**
  ```json
  {
    "code": 400,
    "message": "Invalid username or password",
    "data": null
  }
  ```

### 2. User Registration
- **URL:** `/register`
- **Method:** POST
- **Request Parameters:**
  ```json
  {
    "name": "string",           // Full name
    "age": "integer",           // Age
    "apartment_number": "string", // Apartment number
    "phone_number": "string",    // Phone number
    "password": "string"         // Password
  }
  ```

## Bill Management

### 1. Get User Bills List
- **URL:** `/utility_bills`
- **Method:** GET
- **Request Parameters:** 
  - Optional parameters:
    ```json
    {
      "status": "string",     // Bill status: paid/unpaid
      "bill_type": "string",  // Bill type: water/electricity
      "month": "string"       // Month: YYYY-MM
    }
    ```
- **Response Example:**
  ```json
  {
    "code": 200,
    "data": {
      "bills": [
        {
          "id": 1,
          "bill_type": "Water",
          "amount": 50.5,
          "status": "Unpaid",
          "created_at": "2024-01-01 12:00:00"
        }
      ],
      "total_unpaid": 150.5,
      "total_paid": 200.0
    }
  }
  ```

## Visitor Management

### 1. Visitor Registration
- **URL:** `/visitor/register`
- **Method:** POST
- **Request Parameters:**
  ```json
  {
    "visitor_name": "string",     // Visitor name
    "phone": "string",            // Contact number
    "visit_apartment": "string",  // Apartment to visit
    "purpose": "string",          // Purpose of visit
    "id_number": "string"         // ID card number
  }
  ```

### 2. Mark Visitor Departure
- **URL:** `/visitor/mark_left/<record_id>`
- **Method:** POST
- **Response Example:**
  ```json
  {
    "code": 200,
    "success": true,
    "message": "Visitor status updated"
  }
  ```

## Maintenance Management

### 1. Submit Maintenance Request
- **URL:** `/maintenance/submit`
- **Method:** POST
- **Request Parameters:**
  ```json
  {
    "type": "string",        // Maintenance type
    "description": "string", // Problem description
    "location": "string",    // Specific location
    "contact": "string"      // Contact information
  }
  ```

### 2. Get Maintenance Records
- **URL:** `/maintenance/records`
- **Method:** GET
- **Response Example:**
  ```json
  {
    "code": 200,
    "data": {
      "records": [
        {
          "id": 1,
          "type": "Plumbing",
          "status": "In Progress",
          "submit_time": "2024-01-01 12:00:00",
          "description": "Water pipe leakage",
          "location": "Kitchen"
        }
      ]
    }
  }
  ```

## Announcement Management

### 1. Get Announcement List
- **URL:** `/notices`
- **Method:** GET
- **Response Example:**
  ```json
  {
    "code": 200,
    "data": {
      "notices": [
        {
          "id": 1,
          "title": "Property Notice",
          "content": "Fire drill this Saturday",
          "date": "2024-01-01",
          "icon": "bell"
        }
      ]
    }
  }
  ```

### 2. Create Announcement (Admin)
- **URL:** `/admin/notices/create`
- **Method:** POST
- **Request Parameters:**
  ```json
  {
    "title": "string",    // Announcement title
    "content": "string",  // Announcement content
    "icon": "string"      // Icon type
  }
  ```