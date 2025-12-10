$ErrorActionPreference = "Stop"

$PYTHON_VERSION = "3.11.9"
$URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-amd64.zip"
$DEST_DIR = "$PSScriptRoot\..\python"
$ZIP_FILE = "$DEST_DIR\python.zip"

Write-Host "Setting up Embedded Python $PYTHON_VERSION..."

# 1. Create Directory
if (!(Test-Path $DEST_DIR)) {
    New-Item -ItemType Directory -Force -Path $DEST_DIR | Out-Null
}

# 2. Download
if (!(Test-Path $ZIP_FILE)) {
    Write-Host "Downloading from $URL..."
    Invoke-WebRequest -Uri $URL -OutFile $ZIP_FILE
}

# 3. Extract
Write-Host "Extracting..."
Expand-Archive -Path $ZIP_FILE -DestinationPath $DEST_DIR -Force

# 4. Configure .pth file to allow importing site-packages (required for pip)
# Find the .pth file (e.g., python311._pth)
$pthFile = Get-ChildItem -Path $DEST_DIR -Filter "*._pth" | Select-Object -First 1

if ($pthFile) {
    Write-Host "Configuring $($pthFile.Name) for pip support..."
    $content = Get-Content $pthFile.FullName
    # Uncomment 'import site' if it exists, roughly equivalent to removing the comment #
    $content = $content -replace "#import site", "import site"
    Set-Content -Path $pthFile.FullName -Value $content
}

# 5. Get get-pip.py
$getPip = "$DEST_DIR\get-pip.py"
Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip

Write-Host "Embedded Python installed at $DEST_DIR"
Write-Host "To install pip dependencies, run:"
Write-Host "  .\python\python.exe $getPip"
Write-Host "  .\python\python.exe -m pip install -r requirements.txt"
