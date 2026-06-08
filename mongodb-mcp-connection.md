# MongoDB MCP Connection Info

This workspace file documents the local MongoDB MCP setup created in this session.

## Connection details
- Database: `mcp_demo`
- Collection: `sample`
- Sample document inserted into `mcp_demo.sample`

## Local shell command
```sh
mongosh --eval "const d=db.getSiblingDB('mcp_demo'); d.createCollection('sample'); d.sample.insertOne({createdAt:new Date(), source:'mcp_demo'})"
```

## Verification commands
```sh
mongosh --eval "printjson(db.getMongo().getDBs());"
mongosh --eval "const d=db.getSiblingDB('mcp_demo'); printjson(d.getCollectionNames());"
```

## Notes
If you need a driver connection string, use the local MongoDB URI for your environment. For example:

```text
mongodb://localhost:27017/mcp_demo
```

## Collections
### applications
Document shape:
```json
{
  "application_id": "",
  "business_name": "",
  "owner_name": "",
  "loan_amount": "",
  "decision": ""
}
```

Create command:
```sh
mongosh --eval "const d=db.getSiblingDB('mcp_demo'); d.createCollection('applications'); d.applications.insertOne({application_id:'', business_name:'', owner_name:'', loan_amount:'', decision:''})"
```

### fraud_cases
Document shape:
```json
{
  "case_id": "",
  "reason": "",
  "phone": "",
  "address": ""
}
```

Create command:
```sh
mongosh --eval "const d=db.getSiblingDB('mcp_demo'); d.createCollection('fraud_cases'); d.fraud_cases.insertOne({case_id:'', reason:'', phone:'', address:''})"
```

### businesses
Document shape:
```json
{
  "business_name": "",
  "status": "",
  "previous_loans": []
}
```

Create command:
```sh
mongosh --eval "const d=db.getSiblingDB('mcp_demo'); d.createCollection('businesses'); d.businesses.insertOne({business_name:'', status:'', previous_loans:[]})"
```
