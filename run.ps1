# Script to run management commands for healmymind backend

# Function to show colored output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        
        [Parameter(Mandatory)]
        [string]$Color
    )
    
    $prevColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $prevColor
}

# Function to check prerequisites
function Check-Prerequisites {
    # Check Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "Python not found. Please install Python 3.8 or higher." "Red"
        Write-ColorOutput "Visit: https://www.python.org/downloads/" "Yellow"
        exit 1
    }
    
    # Check Git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "Git not found. Please install Git for Windows." "Red"
        Write-ColorOutput "Visit: https://gitforwindows.org/" "Yellow"
        exit 1
    }
    
    # Check MongoDB
    if (-not (Get-Command mongod -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "MongoDB not found. Please install MongoDB." "Red"
        Write-ColorOutput "Visit: https://www.mongodb.com/try/download/community" "Yellow"
        exit 1
    }
    
    # Check Redis (if installed via WSL)
    if (-not (Get-Command redis-cli -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "Redis not found. Please install Redis using WSL." "Yellow"
        Write-ColorOutput "WSL: sudo apt-get install redis-server" "Yellow"
    }
}

# Function to activate virtual environment
function Activate-Venv {
    if (Test-Path "venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
    } else {
        Write-ColorOutput "Virtual environment not found. Running setup..." "Yellow"
        python -m venv venv
        . .\venv\Scripts\Activate.ps1
        pip install -r requirements.txt
    }
}

# Function to show help
function Show-Help {
    Write-ColorOutput "`nhealmymind Backend Management Script" "Cyan"
    Write-ColorOutput "================================`n" "Cyan"
    
    Write-ColorOutput "Usage: .\run.ps1 <command> [arguments]`n" "White"
    
    Write-ColorOutput "Commands:" "Yellow"
    Write-ColorOutput "  init     - Initialize the project" "White"
    Write-ColorOutput "  manage   - Run Django management commands" "White"
    Write-ColorOutput "  db       - Database management" "White"
    Write-ColorOutput "  test     - Run tests and code quality checks" "White"
    Write-ColorOutput "  deploy   - Deployment commands" "White"
    Write-ColorOutput "  monitor  - Monitoring and maintenance" "White"
    
    Write-ColorOutput "`nExamples:" "Yellow"
    Write-ColorOutput "  .\run.ps1 init" "White"
    Write-ColorOutput "  .\run.ps1 test --coverage" "White"
    Write-ColorOutput "  .\run.ps1 manage runserver" "White"
    Write-ColorOutput "  .\run.ps1 db migrate" "White"
}

# Main script logic
try {
    # Get command from arguments
    $command = $args[0]
    $scriptArgs = $args[1..($args.Length-1)]
    
    # Show help if no command provided
    if (-not $command) {
        Show-Help
        exit 0
    }
    
    # Check prerequisites
    Check-Prerequisites
    
    # Activate virtual environment
    Activate-Venv
    
    # Execute command
    switch ($command) {
        "init" {
            Write-ColorOutput "Initializing project..." "Yellow"
            & bash ./scripts/init.sh @scriptArgs
        }
        "manage" {
            Write-ColorOutput "Running management command..." "Yellow"
            & bash ./scripts/manage.sh @scriptArgs
        }
        "db" {
            Write-ColorOutput "Running database command..." "Yellow"
            & bash ./scripts/db.sh @scriptArgs
        }
        "test" {
            Write-ColorOutput "Running tests..." "Yellow"
            & bash ./scripts/test.sh @scriptArgs
        }
        "deploy" {
            Write-ColorOutput "Running deployment command..." "Yellow"
            & bash ./scripts/deploy.sh @scriptArgs
        }
        "monitor" {
            Write-ColorOutput "Running monitoring command..." "Yellow"
            & bash ./scripts/monitor.sh @scriptArgs
        }
        default {
            Write-ColorOutput "Unknown command: $command" "Red"
            Show-Help
            exit 1
        }
    }
    
    # Check if command was successful
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Command failed with exit code $LASTEXITCODE" "Red"
        exit $LASTEXITCODE
    }
    
} catch {
    Write-ColorOutput "Error: $_" "Red"
    Write-ColorOutput $_.ScriptStackTrace "Red"
    exit 1
}
