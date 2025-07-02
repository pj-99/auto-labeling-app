#!/bin/bash

# Set default MongoDB URI if not provided
MONGO_URI=${MONGO_URI:-"mongodb://localhost:27017/auto-labeling"}

# Create a test user
mongosh "$MONGO_URI" --eval 'db.users.insertOne({
  _id: UUID(),
  name: "Test User",
  email: "test@example.com",
  password: "a_secure_password_hash",
  created_at: new Date(),
  updated_at: new Date()
})'
