// MongoDB initialization script
// Creates application user for the security_api database
db = db.getSiblingDB("security_api");

db.createUser({
  user: "user",
  pwd: "change_this_password_in_production",
  roles: [{ role: "readWrite", db: "security_api" }],
});

print("Application user created for security_api database");

