import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';
import Link from '@mui/material/Link';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import MuiCard from '@mui/material/Card';
import { styled } from '@mui/material/styles';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import DialogContentText from '@mui/material/DialogContentText';
import AppTheme from '../shared-theme/AppTheme';
import ColorModeSelect from '../shared-theme/ColorModeSelect';
// Removed third-party sign up icons
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import { Link as RouterLink } from '@tanstack/react-router';
import { useNavigate } from '@tanstack/react-router';
import { useMutation } from '@tanstack/react-query';
import { ApiError, AuthService } from '../client';

const Card = styled(MuiCard)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignSelf: 'center',
  width: '100%',
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  margin: 'auto',
  boxShadow:
    'hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px',
  [theme.breakpoints.up('sm')]: {
    width: '450px',
  },
  ...theme.applyStyles('dark', {
    boxShadow:
      'hsla(220, 30%, 5%, 0.5) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.08) 0px 15px 35px -5px',
  }),
}));

const SignUpContainer = styled(Stack)(({ theme }) => ({
  height: 'calc((1 - var(--template-frame-height, 0)) * 100dvh)',
  minHeight: '100%',
  padding: theme.spacing(2),
  [theme.breakpoints.up('sm')]: {
    padding: theme.spacing(4),
  },
  '&::before': {
    content: '""',
    display: 'block',
    position: 'absolute',
    zIndex: -1,
    inset: 0,
    backgroundImage:
      'radial-gradient(ellipse at 50% 50%, hsl(210, 100%, 97%), hsl(0, 0%, 100%))',
    backgroundRepeat: 'no-repeat',
    ...theme.applyStyles('dark', {
      backgroundImage:
        'radial-gradient(at 50% 50%, hsla(210, 100%, 16%, 0.5), hsl(220, 30%, 5%))',
    }),
  },
}));

export default function SignUp(props: { disableCustomTheme?: boolean }) {
  const navigate = useNavigate();
  const [emailError, setEmailError] = React.useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = React.useState('');
  const [passwordError, setPasswordError] = React.useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = React.useState('');
  const [confirmPasswordError, setConfirmPasswordError] = React.useState(false);
  const [confirmPasswordErrorMessage, setConfirmPasswordErrorMessage] = React.useState('');
  const [successOpen, setSuccessOpen] = React.useState(false);

  const extractDetail = (body: unknown): string | undefined => {
    if (typeof body === 'object' && body !== null && 'detail' in body) {
      const detail = (body as { detail?: unknown }).detail;
      if (typeof detail === 'string') return detail;
    }
    return undefined;
  };

  const registerMutation = useMutation({
    mutationFn: (payload: { email: string; password: string }) =>
      AuthService.userRegister({ requestBody: payload }),
    onSuccess: () => {
  // Show confirmation dialog; navigate only after user confirms
  setSuccessOpen(true);
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError) {
        // Known server error like existing email
        const detail = extractDetail(err.body);
        setEmailError(true);
        setEmailErrorMessage(detail || 'Failed to register. Please try again.');
      } else {
        setEmailError(true);
        setEmailErrorMessage('Failed to register. Please try again.');
      }
    },
  });

  // No auto-redirect; user must confirm in dialog

  const validateInputs = () => {
    const email = document.getElementById('email') as HTMLInputElement;
    const password = document.getElementById('password') as HTMLInputElement;
  const confirmPassword = document.getElementById('confirmPassword') as HTMLInputElement;

    let isValid = true;

    if (!email.value || !/\S+@\S+\.\S+/.test(email.value)) {
      setEmailError(true);
      setEmailErrorMessage('Please enter a valid email address.');
      isValid = false;
    } else {
      setEmailError(false);
      setEmailErrorMessage('');
    }

    if (!password.value || password.value.length < 8) {
      setPasswordError(true);
      setPasswordErrorMessage('Password must be at least 8 characters long.');
      isValid = false;
    } else {
      setPasswordError(false);
      setPasswordErrorMessage('');
    }

    if (!confirmPassword.value) {
      setConfirmPasswordError(true);
      setConfirmPasswordErrorMessage('Please confirm your password.');
      isValid = false;
    } else if (password.value !== confirmPassword.value) {
      setConfirmPasswordError(true);
      setConfirmPasswordErrorMessage('Passwords do not match.');
      isValid = false;
    } else {
      setConfirmPasswordError(false);
      setConfirmPasswordErrorMessage('');
    }

    return isValid;
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Run client-side validation
    const isValid = validateInputs();
    if (!isValid) return;

    const data = new FormData(event.currentTarget);
    const email = String(data.get('email') || '');
    const password = String(data.get('password') || '');

    // Clear any previous API errors on new attempt
    setEmailError(false);
    setEmailErrorMessage('');

    registerMutation.mutate({ email, password });
  };

  return (
    <AppTheme {...props} disableCustomTheme={true}>
      <CssBaseline enableColorScheme />
      <ColorModeSelect sx={{ position: 'fixed', top: '1rem', right: '1rem' }} />
      <SignUpContainer direction="column" justifyContent="space-between">
        <Card variant="outlined">
          <Box component={RouterLink} to="/" sx={{ display: 'flex', alignItems: 'center', gap: 1, textDecoration: 'none' }}>
            <SolarPowerIcon sx={{ color: 'primary.main', fontSize: 32 }} />
            <Typography
              variant="h6"
              component="div"
              sx={{ fontWeight: 'bold', color: 'primary.main' }}
            >
              Site Analyzer
            </Typography>
          </Box>
          <Typography
            component="h1"
            variant="h4"
            sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
          >
            Sign up
          </Typography>
          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
          >
            <FormControl>
              <FormLabel htmlFor="email">Email</FormLabel>
              <TextField
                required
                fullWidth
                id="email"
                placeholder="your@email.com"
                name="email"
                autoComplete="email"
                variant="outlined"
                error={emailError}
                helperText={emailErrorMessage}
                color={emailError ? 'error' : 'primary'}
              />
            </FormControl>
            <FormControl>
              <FormLabel htmlFor="password">Password</FormLabel>
              <TextField
                required
                fullWidth
                name="password"
                placeholder="••••••"
                type="password"
                id="password"
                autoComplete="new-password"
                variant="outlined"
                error={passwordError}
                helperText={passwordErrorMessage}
                color={passwordError ? 'error' : 'primary'}
              />
            </FormControl>
            <FormControl>
              <FormLabel htmlFor="confirmPassword">Confirm password</FormLabel>
              <TextField
                required
                fullWidth
                name="confirmPassword"
                placeholder="••••••"
                type="password"
                id="confirmPassword"
                autoComplete="new-password"
                variant="outlined"
                error={confirmPasswordError}
                helperText={confirmPasswordErrorMessage}
                color={confirmPasswordError ? 'error' : 'primary'}
              />
            </FormControl>
            {/* Removed marketing opt-in checkbox */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? 'Signing up…' : 'Sign up'}
            </Button>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Typography sx={{ textAlign: 'center' }}>
              Already have an account?{' '}
              <Link component={RouterLink} to="/sign-in" variant="body2" sx={{ alignSelf: 'center' }}>
                Sign in
              </Link>
            </Typography>
          </Box>
        </Card>
      </SignUpContainer>
      <Dialog open={successOpen} onClose={() => setSuccessOpen(false)}>
        <DialogTitle>Registration successful</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Your account has been created. Click Continue to go to the Sign In page.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSuccessOpen(false)}>Stay here</Button>
          <Button
            variant="contained"
            onClick={() => navigate({ to: '/sign-in' })}
            autoFocus
          >
            Continue to Sign In
          </Button>
        </DialogActions>
      </Dialog>
    </AppTheme>
  );
}
