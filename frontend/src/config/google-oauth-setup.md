
# Google OAuth Setup Instructions

## Frontend Setup

### 1. Google Cloud Console Configuration

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google OAuth API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google+ API" or "Google Identity"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized JavaScript origins:
     - `http://localhost:5173` (development)
     - `https://your-production-domain.com` (production)
   - Add authorized redirect URIs:
     - `http://localhost:5173/auth/callback` (development)
     - `https://your-production-domain.com/auth/callback` (production)

4. **Copy Credentials**
   - Copy the Client ID and Client Secret
   - Add to your environment variables

### 2. Environment Variables

Create a `.env.local` file in your project root:

```env
# Google OAuth Configuration
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### 3. Complete the Google OAuth Integration

The Google Sign-In buttons have been added to both login and register forms. To complete the integration:

1. **Install Google OAuth Library**
   ```bash
   npm install @google-cloud/local-auth google-auth-library
   ```

2. **Update the handleGoogleSignIn functions** in `LoginForm.tsx` and `RegisterForm.tsx`:
   ```typescript
   const handleGoogleSignIn = async () => {
     try {
       const googleToken = await signInWithGoogle();
       // Send token to your backend
       const response = await apiClient.googleLogin(googleToken);
       // Handle successful login
     } catch (error) {
       console.error('Google sign-in failed:', error);
     }
   };
   ```

3. **Use the Google Auth Service**
   - The `src/services/google-auth.ts` file contains helper functions
   - Import and use `signInWithGoogle()` function

### 4. Backend Integration

Ensure your backend has the `/api/auth/google` endpoint that:
1. Receives the Google token from frontend
2. Verifies it with Google's servers
3. Creates or finds the user in your database
4. Returns a JWT token for your application

## Security Considerations

1. **HTTPS in Production**: Always use HTTPS in production
2. **Token Validation**: Always verify Google tokens on the backend
3. **CORS Configuration**: Properly configure CORS for your domain
4. **Environment Variables**: Never commit Google Client Secret to version control

## Testing

1. **Development**: Test with `http://localhost:5173`
2. **Production**: Test with your actual domain
3. **Mobile**: Ensure the OAuth flow works on mobile devices

## Troubleshooting

### Common Issues:
1. **"redirect_uri_mismatch"**: Check authorized redirect URIs in Google Console
2. **"unauthorized_client"**: Verify the client ID in environment variables
3. **CORS errors**: Ensure your domain is added to authorized origins

### Debug Steps:
1. Check browser console for errors
2. Verify environment variables are loaded
3. Test with different browsers
4. Check Google Cloud Console settings
