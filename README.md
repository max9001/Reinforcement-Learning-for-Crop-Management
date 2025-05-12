# Reinforcement-Learning-for-Crop-Management

## Running Malmo Python Scripts from Other Directories 

Instructions for temporarily setting environment variables needed to run Malmo Python scripts from a location outside the default Malmo `Python_Examples` folder. These settings apply only to the current terminal/shell session.

### Required Paths

You will need the full paths to two directories within your Malmo installation:

1.  **Python Examples Path:** The directory containing `MalmoPython.pyd` or `MalmoPython.so` (e.g., `/path/to/MalmoPlatform/Python_Examples` or `C:\path\to\MalmoPlatform\Python_Examples`).
2.  **Schemas Path:** The directory containing `Mission.xsd` (e.g., `/path/to/MalmoPlatform/Schemas` or `C:\path\to\MalmoPlatform\Schemas`).

### Instructions per Environment

Replace the placeholder paths below with the actual paths on your system before running the commands.

#### Linux / macOS (Bash/Zsh)

```bash
export PYTHONPATH="/path/to/your/MalmoPlatform/Python_Examples:$PYTHONPATH"
export MALMO_XSD_PATH="/path/to/your/MalmoPlatform/Schemas"
cd /path/to/Reinforcement-Learning-for-Crop-Management
python your_script.py
```

#### Windows (Command Prompt - cmd)

```cmd
set PYTHONPATH=C:\path\to\your\MalmoPlatform\Python_Examples;%PYTHONPATH%
set MALMO_XSD_PATH=C:\path\to\your\MalmoPlatform\Schemas
cd C:\path\to\Reinforcement-Learning-for-Crop-Management
python your_script.py
```

#### Windows (PowerShell)

```powershell
$env:PYTHONPATH = "C:\path\to\your\MalmoPlatform\Python_Examples;" + $env:PYTHONPATH
$env:MALMO_XSD_PATH = "C:\path\to\your\MalmoPlatform\Schemas"
cd C:\path\to\Reinforcement-Learning-for-Crop-Management
python your_script.py
```

---
**Remember:** You must replace the placeholder paths with your specific Malmo installation paths for these commands to work.
