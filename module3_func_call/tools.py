# Simulated employee database
EMPLOYEES = {
    "Rahul": 12,
    "Aisha": 8,
    "John": 15,
    "Fatima": 5
}


def get_leave_balance(employee_name: str):
 
    # Returns the remaining leave balance for an employee.
   
    leave_balance = EMPLOYEES.get(employee_name)

    if leave_balance is None:
        return {
            "status": "error",
            "message": f"Employee '{employee_name}' not found."
        }

    return {
        "status": "success",
        "employee": employee_name,
        "leave_balance": leave_balance
    }

# Tool definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_leave_balance",
            "description": "Get the remaining leave balance of an employee.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee."
                    }
                },
                "required": ["employee_name"]
            }
        }
    }
]

# Tool registry
#"key":value
#"functionName returned by LLM":actualFunctionName
available_functions = {
    "get_leave_balance": get_leave_balance
}