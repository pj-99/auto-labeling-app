#!/bin/bash

# Create a test user
MONGO_COMMAND='db.users.insertOne({
  _id: UUID(),
  name: "Test User",
  email: "test@example.com",
  password: "a_secure_password_hash",
  created_at: new Date(),
  updated_at: new Date()
});'

MONGO_URI=${MONGO_URI}

mongosh "$MONGO_URI" --eval "$MONGO_COMMAND"
