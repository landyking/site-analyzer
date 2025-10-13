import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import CssBaseline from '@mui/material/CssBaseline';
import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
// import './index.css'
import App from './App.tsx'
import { GoogleOAuthProvider } from '@react-oauth/google';

import { ApiError, OpenAPI } from "./client"

OpenAPI.BASE = import.meta.env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

/**
 * Handles API errors by clearing cache and redirecting on auth failures.
 * @param error - The error that occurred.
 */
const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    try {
      // Clear query cache to remove any user-scoped data
      queryClient.clear()
    } catch {
      // no-op
    }
    localStorage.removeItem("access_token")
    window.location.href = "/sign-in"
  }
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
// console.log(clientId)
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CssBaseline />
    <GoogleOAuthProvider clientId={clientId}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </GoogleOAuthProvider>
  </StrictMode>,
)
