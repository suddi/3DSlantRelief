#include <iostream>
#include <windows.h>
#include <string>

using namespace std;

int loadLibrary();
int openPort();
void closePort();
void getSerialNumber();
void getX();
void getY();
void getOffsetX();
void setOffsetX();
void resetOffsetX();
void getOffsetY();
void setOffsetY();
void resetOffsetY();
long getTime();

typedef int (__stdcall * pIIIO)(int); 
typedef int (__stdcall * pVIIO)(void); 
typedef float (__stdcall * pVIFO)(void);

HINSTANCE hinstLib;
pIIIO Open;
pVIIO Close;
pVIIO GetSerialNumber;
pVIFO GetX;
pVIFO GetY;
pVIFO GetOffsetX;
pVIIO SetOffsetX;
pVIIO ResetOffsetX;
pVIFO GetOffsetY;
pVIIO SetOffsetY;
pVIIO ResetOffsetY;

const int PORT_NUM = 22;

int main(int argc, char* args[]) {
    bool quit = false;
    string py_message = "";

    bool load = loadLibrary();
    if (load) {
        int status = openPort();
        if (status == 0) {
            while (!quit) {
                cin >> py_message;

                if (py_message == "getSerialNumber") {
                    getSerialNumber();
                } else if (py_message == "getX") {
                    getX();
                } else if (py_message == "getY") {
                    getY();
                } else if (py_message == "getOffsetX") {
                    getOffsetX();
                } else if (py_message == "setOffsetX") {
                    setOffsetX();
                } else if (py_message == "resetOffsetX") {
                    resetOffsetX();
                } else if (py_message == "getOffsetY") {
                    getOffsetY();
                } else if (py_message == "setOffsetY") {
                    setOffsetY();
                } else if (py_message == "resetOffsetY") {
                    resetOffsetY();
                } else if (py_message == "quit") {
                    quit = true;
                } else {
                    cout << "Command not recognized" << endl;
                }
            }
            closePort();
        }
    }
    return 0;
}

int loadLibrary() {
    hinstLib = LoadLibrary(TEXT("NSxxDOG_DLL.dll"));
    if (hinstLib != NULL) {
        return true;
    } else {
        return false;
    }
}

int openPort() {
    FARPROC lpfnOpen = GetProcAddress(HMODULE (hinstLib),"Open"); 
    Open = pIIIO(lpfnOpen);

    return Open(PORT_NUM);
}

void closePort() {
    FARPROC lpfnClose = GetProcAddress(HMODULE (hinstLib),"Close"); 
    Close = pVIIO(lpfnClose);

    Close();
    FreeLibrary(hinstLib);
}

void getSerialNumber() {
    FARPROC lpfnGetSerialNumber = GetProcAddress(HMODULE (hinstLib),"GetSerialNumber"); 
    GetSerialNumber = pVIIO(lpfnGetSerialNumber);

    // printf("%d\n", GetSerialNumber());
    cout << GetSerialNumber() << endl;
}

void getX() {
    FARPROC lpfnGetX = GetProcAddress(HMODULE (hinstLib),"GetX"); 
    GetX = pVIFO(lpfnGetX);

    // printf("%f\n", GetX());    
    cout << GetX() << endl;
}

void getY() {
    FARPROC lpfnGetY = GetProcAddress(HMODULE (hinstLib),"GetY"); 
    GetY = pVIFO(lpfnGetY);

    // printf("%f\n", GetY());
    cout << GetY() << endl;
}

void getOffsetX() {
    FARPROC lpfnGetOffsetX = GetProcAddress(HMODULE (hinstLib),"GetOffsetX"); 
    GetOffsetX = pVIFO(lpfnGetOffsetX);

    // printf("%f\n", GetOffsetX());
    cout << GetOffsetX() << endl;
}

void setOffsetX() {
    FARPROC lpfnSetOffsetX = GetProcAddress(HMODULE (hinstLib),"SetOffsetX"); 
    SetOffsetX = pVIIO(lpfnSetOffsetX);

    // printf("%d\n", SetOffsetX());
    cout << SetOffsetX() << endl;
}

void resetOffsetX() {
    FARPROC lpfnResetOffsetX = GetProcAddress(HMODULE (hinstLib),"ResetOffsetX"); 
    ResetOffsetX = pVIIO(lpfnResetOffsetX);

    // printf("%d\n", ResetOffsetX());
    cout << ResetOffsetX() << endl;
}

void getOffsetY() {
    FARPROC lpfnGetOffsetY = GetProcAddress(HMODULE (hinstLib),"GetOffsetY"); 
    GetOffsetY = pVIFO(lpfnGetOffsetY);

    // printf("%f\n", GetOffsetY());
    cout << GetOffsetY() << endl;
}

void setOffsetY() {
    FARPROC lpfnSetOffsetY = GetProcAddress(HMODULE (hinstLib),"SetOffsetY"); 
    SetOffsetY = pVIIO(lpfnSetOffsetY);

    // printf("%d\n", SetOffsetY());
    cout << SetOffsetY() << endl;
}

void resetOffsetY() {
    FARPROC lpfnResetOffsetY = GetProcAddress(HMODULE (hinstLib),"ResetOffsetY"); 
    ResetOffsetY = pVIIO(lpfnResetOffsetY);

    // printf("%d\n", ResetOffsetY());
    cout << ResetOffsetY() << endl;
}

long getTime() {
    FILETIME ft;
    LARGE_INTEGER li;

    GetSystemTimeAsFileTime(&ft);
    li.LowPart = ft.dwLowDateTime;
    li.HighPart = ft.dwHighDateTime;

    long ret = li.QuadPart;
    ret -= 116444736000000000LL; /* Convert from file time to UNIX epoch time. */
    ret /= 10000; /* From 100 nano seconds (10^-7) to 1 millisecond (10^-3) intervals */

    return ret;
}
