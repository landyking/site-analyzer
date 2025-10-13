import Alert from "@mui/material/Alert";

/**
 * Displays demo account information when in demo mode.
 * @returns An alert component with demo credentials or null.
 */
export function ShowDemo() {
    if (import.meta.env.VITE_RELEASE_DEMO === '1') {
        return (
            <Alert severity="warning" sx={{ mb: 0 }}>
                Note: The system is in demo mode. You can explore the app using our demo account. 
                Username: <strong>{import.meta.env.VITE_RELEASE_DEMO_USERNAME}</strong> and password: <strong>{import.meta.env.VITE_RELEASE_DEMO_PASSWORD}</strong>.
            </Alert>
        );
    }
    return null;
}