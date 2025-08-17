import { useMemo, useState } from 'react';
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
import SuitabilityFactorsStep, { type SuitabilityFactorsStepHandle } from './new-map/SuitabilityFactorsStep';
import ConfirmationStep, { type ConfirmationStepHandle } from './new-map/ConfirmationStep';
import { useRef } from 'react';

export default function NewMap() {
  const { alert } = useDialogs();
  const steps = useMemo(
    () => ['base info', 'Constraint factors', 'Suitability factors', 'Confirmation'],
    [],
  );

  const [activeStep, setActiveStep] = useState(0);
  const [form, setForm] = useState({
    // base info
    name: '', // submit as name
    district: '', // submit as district (code)
    // placeholders for next steps (will be refined later)
  constraints: [] as ConstraintFactorsValue,
    suitability: '',
    confirmation: '',
    constraintsSelect: '',
    suitabilitySelect: '',
    confirmationSelect: '',
  });

  // Step-to-field mapping now handled inline per component props.

  const baseRef = useRef<BaseInfoStepHandle>(null);
  const constraintRef = useRef<ConstraintFactorsStepHandle>(null);
  const suitabilityRef = useRef<SuitabilityFactorsStepHandle>(null);
  const confirmRef = useRef<ConfirmationStepHandle>(null);

  function validateStep(stepIndex: number) {
    switch (stepIndex) {
      case 0:
        return baseRef.current?.validate() ?? true;
      case 1:
        return constraintRef.current?.validate() ?? true;
      case 2:
        return suitabilityRef.current?.validate() ?? true;
      case 3:
        return confirmRef.current?.validate() ?? true;
      default:
        return true;
    }
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

    // Show dialog with all input values as JSON and remain on the last step
    const json = JSON.stringify(form, null, 2);
    await alert(
      <Box component="pre" sx={{ m: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
        {json}
      </Box>,
      { title: 'New Map Inputs' },
    );
  }

  function renderStepContent(stepIndex: number) {
    switch (stepIndex) {
      case 0:
        return (
          <BaseInfoStep
            ref={baseRef}
            value={{ name: form.name, district: form.district }}
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
            textValue={form.suitability}
            onTextChange={(v) => setForm((f) => ({ ...f, suitability: v }))}
            selectValue={form.suitabilitySelect}
            onSelectChange={(v) => setForm((f) => ({ ...f, suitabilitySelect: v }))}
          />
        );
      case 3:
      default:
        return (
          <ConfirmationStep
            ref={confirmRef}
            textValue={form.confirmation}
            onTextChange={(v) => setForm((f) => ({ ...f, confirmation: v }))}
            selectValue={form.confirmationSelect}
            onSelectChange={(v) => setForm((f) => ({ ...f, confirmationSelect: v }))}
          />
        );
    }
  }

  return (
    <PageContainer title="New Map" breadcrumbs={[{ title: 'New Map' }]}>
      <Stack spacing={3}>
        <Typography color="text.secondary">
          Start creating a new map from data sources and layers.
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
                  <Button variant="contained" onClick={handleNext}>
                    Next
                  </Button>
                ) : (
                  <Button variant="contained" color="primary" onClick={handleSubmit}>
                    Submit
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
