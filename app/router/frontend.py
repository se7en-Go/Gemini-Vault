import httpx
from fastapi import APIRouter, Request, Form, Depends, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

frontend_router = APIRouter()

templates = Jinja2Templates(directory="templates")

@frontend_router.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def read_root_page(request: Request):
    """
    Serves the home/landing page.
    """
    return templates.TemplateResponse("home.html", {"request": request})

@frontend_router.get("/login", response_class=HTMLResponse, tags=["Frontend"])
async def get_login_page(request: Request):
    """
    Serves the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@frontend_router.post("/login", response_class=HTMLResponse, tags=["Frontend"])
async def post_login_page(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Handles the login form submission.
    """
    # We call our own API to get a token
    async with httpx.AsyncClient() as client:
        try:
            api_url = str(request.base_url) + "auth/token"
            response = await client.post(
                api_url,
                data={"username": username, "password": password}
            )
            response.raise_for_status() # Raise an exception for bad status codes
            
            token_data = response.json()
            
            # Redirect to dashboard and set the token in a cookie
            redirect_response = RedirectResponse(url="/dashboard", status_code=303)
            redirect_response.set_cookie(key="access_token", value=f"Bearer {token_data['access_token']}", httponly=True)
            return redirect_response

        except httpx.HTTPStatusError as e:
            # If login fails, re-render the login page with an error
            error_message = "Invalid username or password."
            if e.response.status_code == 400:
                 error_message = "Invalid username or password."
            return templates.TemplateResponse("login.html", {"request": request, "error": error_message})

@frontend_router.post("/logout", tags=["Frontend"])
async def logout_and_redirect():
    """
    Handles logout by clearing the cookie and redirecting.
    """
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

@frontend_router.get("/register", response_class=HTMLResponse, tags=["Frontend"])
async def get_register_page(request: Request):
    """
    Serves the registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@frontend_router.post("/register", response_class=HTMLResponse, tags=["Frontend"])
async def post_register_page(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Handles the registration form submission.
    """
    async with httpx.AsyncClient() as client:
        try:
            api_url = str(request.base_url) + "auth/users/"
            response = await client.post(
                api_url,
                json={"email": email, "username": username, "password": password}
            )
            response.raise_for_status()
            
            return templates.TemplateResponse("register.html", {"request": request, "success": "Account created successfully!"})

        except httpx.HTTPStatusError as e:
            error_message = "An unknown error occurred."
            if e.response.status_code == 400:
                error_message = e.response.json().get("detail", "Registration failed.")
            return templates.TemplateResponse("register.html", {"request": request, "error": error_message})

@frontend_router.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def get_dashboard_page(request: Request, access_token: Optional[str] = Cookie(None)):
    """
    Serves the user dashboard, showing user info and API keys.
    """
    if not access_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    headers = {"Authorization": access_token}
    
    async with httpx.AsyncClient() as client:
        try:
            # Get user details
            user_url = str(request.base_url) + "auth/users/me"
            user_response = await client.get(user_url, headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()

            # Get user API keys
            keys_url = str(request.base_url) + "api-keys/"
            keys_response = await client.get(keys_url, headers=headers)
            keys_response.raise_for_status()
            api_keys_data = keys_response.json()

            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": user_data,
                "api_keys": api_keys_data
            })
        except httpx.HTTPStatusError:
            # If token is invalid or expired, redirect to login
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@frontend_router.post("/dashboard/create-api-key", tags=["Frontend"])
async def handle_create_api_key(request: Request, access_token: Optional[str] = Cookie(None)):
    """
    Handles the form post to create a new API key.
    """
    if not access_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    headers = {"Authorization": access_token}
    
    async with httpx.AsyncClient() as client:
        try:
            keys_url = str(request.base_url) + "api-keys/"
            response = await client.post(keys_url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            # Handle potential errors, e.g., if key creation fails
            pass
    
    # Redirect back to the dashboard to show the new key
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
