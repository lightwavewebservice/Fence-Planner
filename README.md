# Farm Fence Planner (NZD excl. GST)

Django 4.x web application to calculate farm fence material requirements and costs, export professional PDF/Excel reports, and manage regional pricing with optional scraping. Target region is Southland, New Zealand. All prices are in NZD and exclude GST.

## Features
- 🧮 Calculator for posts, wire, battens, labor, and costs
- 💾 Persisted calculations with detail view
- 📄 Exports: PDF (ReportLab) and Excel (openpyxl)
- ⚙️ Settings tab to manage materials, price sources, and auto-update toggle
- 🔌 Hot wire support: specify number of hot wires (1-20)
- 🦌 Deer fence support with configurable netting and posts
- 📏 Staples calculation for non-hot wires and netting
- 🏗️ Customizable build rate (m/hr) for labor calculations

## Tech Stack
- **Backend**: Django 4.x
- **Database**: SQLite (dev), PostgreSQL (production-ready)
- **Frontend**: HTML, Tailwind CSS (CDN)
- **Dependencies**: ReportLab, openpyxl, requests, beautifulsoup4

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.8+
- Git
- Windows 10/11 or Windows Server 2019/2022

### Local Development Setup

1. **Clone the repository**
   ```powershell
   git clone https://github.com/lightwavewebservice/Fence-Planner.git
   cd Fence-Planner

2. **Set up virtual environment**
   ```powershell
   # Create and activate virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure database and settings**
   ```powershell
   # Run migrations
   python manage.py migrate
   
   # Load initial data
   python manage.py seed_initial_data
   
   # Create superuser (optional, for admin access)
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```powershell
   python manage.py runserver
   ```
   - Access the app at: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 🖥️ Windows Server Deployment

### Prerequisites
- Windows Server 2019/2022
- Python 3.8+
- IIS with URL Rewrite Module
- Web Platform Installer
- Git for Windows

### Installation Steps

1. **Install Web Server (IIS) Role**
   - Open Server Manager
   - Click "Add roles and features"
   - Select "Role-based or feature-based installation"
   - Select your server
   - Check "Web Server (IIS)" role
   - Add required features:
     - .NET Extensibility 4.7+
     - ASP.NET 4.7+
     - ISAPI Extensions
     - ISAPI Filters
     - CGI
     - Static Content
     - Default Document
     - HTTP Errors
     - Static Content Compression
     - HTTP Logging
     - Request Monitor
     - URL Authorization
     - Request Filtering
     - Static Content

2. **Install URL Rewrite Module**
   - Download from: https://www.iis.net/downloads/microsoft/url-rewrite
   - Run the installer as administrator
   - Verify installation in IIS Manager under "Modules"

3. **Install Python**
   - Download Python 3.8+ 64-bit from python.org
   - During installation:
     - Check "Add Python to PATH"
     - Select "Customize installation"
     - Check "pip" and "Add Python to environment variables"
     - Install for all users
   - Install required build tools:
     ```powershell
     winget install -e --id Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
     ```

4. **Deploy Application**
   ```powershell
   # Create web root directory
   New-Item -Path "C:\inetpub\fence-planner" -ItemType Directory -Force
   
   # Clone repository
   cd C:\inetpub\fence-planner
   git clone https://github.com/lightwavewebservice/Fence-Planner.git .
   
   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Install dependencies
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install wfastcgi
   
   # Configure database
   python manage.py migrate
   python manage.py seed_initial_data
   python manage.py collectstatic --noinput
   
   # Create superuser (optional)
   python manage.py createsuperuser
   ```

5. **Configure IIS**
   - Open IIS Manager as Administrator
   - Right-click "Sites" → "Add Website"
   - Site name: "Fence Planner"
   - Physical path: `C:\inetpub\fence-planner`
   - Set port (e.g., 8080) or hostname
   - Click "OK"
   
   **Configure Application Pool:**
   - In IIS Manager, go to "Application Pools"
   - Find your site's app pool (should be named after your site)
   - Right-click → "Advanced Settings"
   - Set:
     - .NET CLR version: "No Managed Code"
     - Identity: ApplicationPoolIdentity
     - Start Mode: AlwaysRunning
     - Idle Time-out: 0 (disabled)
     - Regular Time Interval: 0 (disabled)
     - Enable 32-Bit Applications: False

6. **Configure web.config**
   Create/update `web.config` in your project root:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <configuration>
     <appSettings>
       <add key="PYTHONPATH" value="C:\inetpub\fence-planner" />
       <add key="WSGI_HANDLER" value="django.core.wsgi.get_wsgi_application()" />
       <add key="DJANGO_SETTINGS_MODULE" value="farm_fence_planner.settings" />
     </appSettings>
     <system.webServer>
       <handlers>
         <add name="Python FastCGI" 
              path="*" 
              verb="*" 
              modules="FastCgiModule" 
              scriptProcessor="C:\inetpub\fence-planner\venv\Scripts\python.exe|C:\inetpub\fence-planner\venv\Lib\site-packages\wfastcgi.py" 
              resourceType="Unspecified" 
              requireAccess="Script" />
       </handlers>
       <httpErrors errorMode="Detailed" />
       <security>
         <requestFiltering>
           <requestLimits maxAllowedContentLength="1073741824" />
         </requestFiltering>
       </security>
       <staticContent>
         <mimeMap fileExtension=".woff2" mimeType="font/woff2" />
         <mimeMap fileExtension=".woff" mimeType="font/woff" />
         <mimeMap fileExtension=".json" mimeType="application/json" />
       </staticContent>
     </system.webServer>
     <system.web>
       <customErrors mode="Off" />
       <compilation debug="true" />
       <httpRuntime maxRequestLength="1048576" />
     </system.web>
   </configuration>
   ```

7. **Set Folder Permissions**
   ```powershell
   $acl = Get-Acl "C:\inetpub\fence-planner"
   $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS AppPool\\Fence Planner", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
   $acl.SetAccessRule($accessRule)
   Set-Acl "C:\\inetpub\\fence-planner" $acl
   
   # Grant permissions to static and media directories
   $dirs = @("static", "media", "db.sqlite3")
   foreach ($dir in $dirs) {
       $path = Join-Path "C:\\inetpub\\fence-planner" $dir
       if (Test-Path $path) {
           $acl = Get-Acl $path
           $acl.SetAccessRule($accessRule)
           Set-Acl $path $acl
       }
   }
   ```

8. **Enable wfastcgi**
   ```powershell
   cd C:\inetpub\fence-planner\venv\Scripts
   .\python.exe -m wfastcgi-enable
   ```
   This will output a handler string. Make sure it matches the scriptProcessor in web.config.

9. **Start the Site**
   - In IIS Manager, select your site
   - Click "Browse Website" or access it via the configured URL
   - Check the Windows Event Viewer for detailed error messages if needed

## 🔧 Maintenance

### Updating the Application
```powershell
# Navigate to project directory
cd C:\inetpub\fence-planner

# Stop the site (optional but recommended)
iisreset /stop

# Pull latest changes
git pull origin master

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Update dependencies
pip install -r requirements.txt

# Apply database updates
python manage.py migrate
python manage.py collectstatic --noinput

# Restart the site
iisreset /start
```

### Backing Up Data
```powershell
# Create backup directory
$backupDir = "C:\\backups\\fence-planner-$(Get-Date -Format 'yyyyMMdd')"
New-Item -ItemType Directory -Path $backupDir -Force

# Backup SQLite database
Copy-Item -Path "C:\\inetpub\\fence-planner\\db.sqlite3" -Destination "$backupDir\\db.sqlite3"

# Backup media files (if any)
if (Test-Path "C:\\inetpub\\fence-planner\\media") {
    Compress-Archive -Path "C:\\inetpub\\fence-planner\\media\*" -DestinationPath "$backupDir\\media-$(Get-Date -Format 'yyyyMMdd').zip"
}

# For production with PostgreSQL, use pg_dump
# pg_dump -U username -d dbname > $backupDir\\db_backup_$(Get-Date -Format 'yyyyMMdd').sql

# Optionally, copy backups to a network location
# Copy-Item -Path "$backupDir\\*" -Destination "\\network\backup\fence-planner\" -Recurse -Force
```

### Monitoring and Logs
- Check application logs in: `C:\inetpub\logs\LogFiles`
- Check Windows Event Viewer for system and application events
- For detailed Django errors, set `DEBUG = True` in settings.py (temporarily)

## 📄 License
This project is proprietary software. All rights reserved.
4. Run the dev server:
```
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

## Notes
- Currency: NZD, prices exclude GST.
- Region defaults: Southland. See `PriceSource` and `ScrapingSettings` models.
- Constants in `farm_fence_planner/settings.py`:
  - `LABOR_RATE_PER_HOUR = 55.0`
  - `WIRE_ROLL_LENGTH = 500`
  - `BUILD_RATE_METERS_PER_HOUR = 20`
  - Staples configuration:
    - `STAPLES_ENABLED = True`
    - `STAPLES_MATERIAL_NAME = 'U Staples (Box of 2000)'`
    - `STAPLES_PER_BOX = 2000`
    - `STAPLES_DEFAULT_PRICE = 183.99`
    - `STAPLES_PER_WIRE_PER_LINE_POST = 1`
    - `STAPLES_PER_WIRE_PER_END_POST = 2`
    - `STAPLES_PER_POST_FOR_NETTING = 4`

## Tests
Run unit and integration tests:
```
python manage.py test
```

## Disclaimer
All calculations and material prices provided by this application are indicative only and may change. Prices are sourced from suppliers and are subject to market fluctuations, regional variations, and supplier updates. Always verify current prices and requirements with your local suppliers before making purchasing decisions. The developers assume no liability for any discrepancies or decisions made based on the outputs of this tool.

## Future work
- Real supplier scraping adapters (e.g., Farmlands Invercargill) with retries and HTML fixtures
- Periodic scraping via `django-crontab` or Celery using `ScrapingSettings.default_scrape_interval_hours`
- Postgres + Docker for prod-like local dev
