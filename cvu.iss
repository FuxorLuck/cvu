; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Citra Valentin Updater"
; MyAppVersion defined by iscc.
#define MyAppPublisher "Valentin Vanelslande"
#define MyAppURL "https://github.com/vvanelslande/cvu"
#define MyAppExeName "cvu.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{1F8CDC78-17E5-4A8D-800D-7E6C4966BFC7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\cvu
DisableProgramGroupPage=yes
LicenseFile=license.txt
PrivilegesRequired=lowest
OutputBaseFilename=cvu_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=citra.ico
ChangesEnvironment=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\cvu.exe"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: SetInstallDir
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\Citra\Citra Valentin"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Citra Valentin"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName:"CVU_INSTALL_DIR"; ValueData:"{code:GetInstallDir}"; Flags: preservestringtype uninsdeletevalue

[Code]
var
  Page: TInputDirWizardPage;

#ifdef UNICODE
  #define AW "W"
#else
  #define AW "A"
#endif

function SetEnvironmentVariable(lpName: string; lpValue: string): BOOL;
  external 'SetEnvironmentVariable{#AW}@kernel32.dll stdcall';

procedure InitializeWizard;
begin
  Page := CreateInputDirPage(wpSelectDir, 'Select Citra Valentin Installation Directory', '', '', False, 'New Folder');
  Page.Add('')
  Page.Values[0] := GetEnv('CVU_INSTALL_DIR')
  if (Page.Values[0] = '') then begin
    Page.Values[0] := ExpandConstant('{localappdata}\citra-valentin')
  end;
end;

function GetInstallDir(Param: string) : string;
begin
  Result := Page.Values[0];
end;

procedure SetInstallDir;
begin
  SetEnvironmentVariable('CVU_INSTALL_DIR', GetInstallDir(''))
end;