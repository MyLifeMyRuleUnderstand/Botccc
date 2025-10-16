# Universal File Host — Vercel-ready package

This package contains a Flask-only app intended to be deployed on **Vercel** as a serverless function.

Important notes:
- This **does not** run the Telegram bot polling (long-running processes are not supported on Vercel).
- Use this service to serve already-uploaded files. File uploads & bot polling must run elsewhere (e.g., a background VM, Railway, Render, or Termux).
- Put uploaded files under the directory defined by the `UPLOADS_DIR` environment variable (default `uploads/`), following the structure:
  ```
  uploads/
    <user_id>/
      file1.bin
      file2.txt
  ```
- Each file will be accessible at `/api/file/<md5(user_id + "_" + file_name)>`

Deployment:
1. Install Vercel CLI: `npm i -g vercel`
2. In this folder, run `vercel` and follow prompts.
3. Set environment variables on Vercel if needed (UPLOADS_DIR, BASE_URL).

