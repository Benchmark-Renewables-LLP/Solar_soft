
// Google OAuth integration for frontend
export const initGoogleAuth = () => {
  const script = document.createElement('script');
  script.src = 'https://apis.google.com/js/platform.js';
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
};

export const signInWithGoogle = (): Promise<string> => {
  return new Promise((resolve, reject) => {
    if (typeof window.gapi === 'undefined') {
      reject(new Error('Google API not loaded'));
      return;
    }

    window.gapi.load('auth2', () => {
      const auth2 = window.gapi.auth2.init({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID
      });

      auth2.signIn().then((googleUser: any) => {
        const idToken = googleUser.getAuthResponse().id_token;
        resolve(idToken);
      }).catch(reject);
    });
  });
};

// Type declarations for Google API
declare global {
  interface Window {
    gapi: any;
  }
}
