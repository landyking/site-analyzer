import { useMemo, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import PageContainer from './PageContainer';
import { useDialogs } from '../hooks/useDialogs/useDialogs';
import BaseInfoStep, { type BaseInfoStepHandle } from './new-map/BaseInfoStep';
import ConstraintFactorsStep, { type ConstraintFactorsStepHandle, type ConstraintFactorsValue } from './new-map/ConstraintFactorsStep';
import SuitabilityFactorsStep, { type SuitabilityFactorsStepHandle, type SuitabilityFactorsValue } from './new-map/SuitabilityFactorsStep';
import ConfirmationStep, { type ConfirmationStepHandle } from './new-map/ConfirmationStep';
import { useRef } from 'react';
import { UserService } from '../../client/sdk.gen';
import type { CreateMapTaskReq } from '../../client/types.gen';

export default function NewMap() {
  const { alert, confirm } = useDialogs();
  const navigate = useNavigate();
  const steps = useMemo(
  () => ['Basics', 'Constraints', 'Suitability & weights', 'Review & create'],
    [],
  );

  const [activeStep, setActiveStep] = useState(0);
  const [form, setForm] = useState({
    // base info
  name: '', // submit as name
  district: '', // submit as district (code)
  districtLabel: '',
    // placeholders for next steps (will be refined later)
  constraints: [] as ConstraintFactorsValue,
  suitability: [] as SuitabilityFactorsValue,
  });
  const [submitting, setSubmitting] = useState(false);

  // Step-to-field mapping now handled inline per component props.

  const baseRef = useRef<BaseInfoStepHandle>(null);
  const constraintRef = useRef<ConstraintFactorsStepHandle>(null);
  const suitabilityRef = useRef<SuitabilityFactorsStepHandle>(null);
  const confirmRef = useRef<ConfirmationStepHandle>(null);

  function validateStep(stepIndex: number) {
    // console.log('Validating step:', stepIndex);
    let result = false;
    switch (stepIndex) {
      case 0:
        result = baseRef.current?.validate() ?? true;
        break;
      case 1:
        result = constraintRef.current?.validate() ?? true;
        break;
      case 2:
        result = suitabilityRef.current?.validate() ?? true;
        break;
      case 3:
        result = confirmRef.current?.validate() ?? true;
        break;
      default:
        result = true;
    }
    // console.log('Validation result for step', stepIndex, ':', result);
    return result;
  }

  function handleNext() {
    if (!validateStep(activeStep)) return;
    setActiveStep((s) => Math.min(s + 1, steps.length - 1));
  }

  function handleBack() {
    setActiveStep((s) => Math.max(s - 1, 0));
  }

  async function handleSubmit() {
    // Validate the last step
    if (!validateStep(activeStep)) return;
    // Confirm before submitting
    const ok = await confirm('Are you sure you want to create this map?', {
      title: 'Confirm submission',
      okText: 'Create map',
      cancelText: 'Cancel',
      severity: 'warning',
    });
    if (!ok) return;
    const payload: CreateMapTaskReq = {
      name: form.name,
      district_code: form.district,
      constraint_factors: form.constraints.map((c) => ({ kind: c.kind, value: c.value })),
      suitability_factors: form.suitability.map((s) => ({ kind: s.kind, weight: s.weight, ranges: s.ranges })),
    };
    try {
      setSubmitting(true);
      const resp = await UserService.userCreateMapTask({ requestBody: payload });
      const taskId = resp.data?.id ?? undefined;
      await alert(
        <Box>
          <Typography component="div" sx={{ mb: 1 }}>Your map task has been created.</Typography>
          {taskId ? (
            <Typography component="div" color="text.secondary">Task ID: {taskId}</Typography>
          ) : null}
        </Box>,
        { title: 'Submitted' },
      );
      navigate({ to: '/dashboard/my-maps' });
  } catch {
      // Errors are also handled globally; show a simple message here
      await alert('Failed to submit. Please try again.', { title: 'Error' });
    } finally {
      setSubmitting(false);
    }
  }

  function renderStepContent(stepIndex: number) {
    switch (stepIndex) {
      case 0:
        return (
          <BaseInfoStep
            ref={baseRef}
            value={{ name: form.name, district: form.district, districtLabel: form.districtLabel }}
            onChange={(v) => setForm((f) => ({ ...f, ...v }))}
          />
        );
      case 1:
        return (
          <ConstraintFactorsStep
            ref={constraintRef}
            value={form.constraints}
            onChange={(v) => setForm((f) => ({ ...f, constraints: v }))}
          />
        );
      case 2:
        return (
          <SuitabilityFactorsStep
            ref={suitabilityRef}
            value={form.suitability}
            onChange={(v) => setForm((f) => ({ ...f, suitability: v }))}
            districtCode={form.district}
          />
        );
      case 3:
      default:
        return (
          <ConfirmationStep
            ref={confirmRef}
            data={{
              name: form.name,
              district: form.district,
              districtLabel: form.districtLabel,
              constraints: form.constraints,
              suitability: form.suitability,
            }}
          />
        );
    }
  }

  return (
    <PageContainer title="New Map" breadcrumbs={[{ title: 'New Map' }]}> 
      <Stack spacing={3}>
        <Typography color="text.secondary">
          Define basics, set constraints, configure suitability weights and scoring, then review and create.
        </Typography>

        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Paper variant="outlined" sx={{ p: 3 }}>
          <Stack spacing={2}>
            {renderStepContent(activeStep)}

            {activeStep === 0 ? (
              <Box display="flex" justifyContent="flex-end" mt={1}>
                <Button variant="contained" onClick={handleNext}>
                  Next
                </Button>
              </Box>
            ) : (
              <Box display="flex" justifyContent="space-between" mt={1}>
                <Button variant="outlined" onClick={handleBack}>
                  Previous
                </Button>
                {activeStep < steps.length - 1 ? (
                  <Button variant="contained" onClick={handleNext} disabled={submitting}>
                    Next
                  </Button>
                ) : (
                  <Button variant="contained" color="primary" onClick={handleSubmit} disabled={submitting}>
                    Create map
                  </Button>
                )}
              </Box>
            )}
          </Stack>
        </Paper>
      </Stack>
    </PageContainer>
  );
}
