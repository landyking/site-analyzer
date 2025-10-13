import Alert from "@mui/material/Alert";

/**
 * Displays read-only mode warning when the system is in demo read-only state.
 * @returns An alert component with read-only mode information or null.
 */
export function ReadOnlyMode() {
    if (import.meta.env.VITE_RELEASE_READ_ONLY === '1') {
        return (
            <Alert severity="warning" sx={{ mb: 0 }}>
                Note: Due to limitations of the demo server's performance, the system is currently in read-only mode.
                Users cannot create or modify maps but can browse and analyze existing sample map tasks.
                To experience the full functionality, please refer to our <a href="https://github.com/landyking/site-analyzer">GitHub</a> repository to self-deploy.
            </Alert>
        );
    }
    return null;
}