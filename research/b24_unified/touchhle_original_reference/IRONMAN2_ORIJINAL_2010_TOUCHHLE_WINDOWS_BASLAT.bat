@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist "%~dp0touchHLE.exe" (
  echo [HATA] touchHLE.exe bu klasorde yok.
  echo Resmi touchHLE Windows surumunu https://github.com/touchHLE/touchHLE/releases adresinden indirip dosyalari bu klasore cikar.
  pause
  exit /b 1
)
if "%~1"=="" (
  set "GAME="
  for %%F in ("%~dp0*.ipa") do if not defined GAME set "GAME=%%~fF"
) else (
  set "GAME=%~f1"
)
if not defined GAME (
  echo [HATA] Orijinal Iron Man 2 1.0.0 IPA dosyasini bu klasore koy veya BAT uzerine surukle.
  pause
  exit /b 2
)
if not exist "%GAME%" (
  echo [HATA] IPA bulunamadi: "%GAME%"
  pause
  exit /b 3
)
echo Orijinal iOS 1.0.0 oyununu touchHLE ile calistiriyoruz.
echo Dosya: "%GAME%"
echo Bu gercek iOS oyunudur; Vita portunun testi degildir.
echo Ekran goruntusu: Windows + Shift + S
echo.
"%~dp0touchHLE.exe" "%GAME%" --landscape-left --print-fps
set "RC=%ERRORLEVEL%"
echo.
echo Emulator kapandi / donus kodu %RC%.
pause
exit /b %RC%
