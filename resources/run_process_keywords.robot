*** Settings ***
Library    OperatingSystem

*** Keywords ***
Run Python Script
    ${result}=    Run And Return Rc    python my_script.py arg1 arg2
    ${output}=    Run And Return Rc    python my_script.py arg1 arg2    WITH OUTPUT
    Log    Result Code: ${result}
    Log    Output: ${output}
