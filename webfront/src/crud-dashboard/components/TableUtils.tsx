import Stack from '@mui/material/Stack';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import type { SelectChangeEvent } from '@mui/material/Select';

// Props for reusable compact pagination/footer
export interface CompactPaginationProps {
  page: number;
  pageSize: number;
  total: number; // total items
  pageCount: number; // computed page count
  rangeStart: number;
  rangeEnd: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  pageSizeOptions?: number[];
  disabled?: boolean;
}

export function CompactPagination({
  page, pageSize, total, pageCount, rangeStart, rangeEnd,
  onPageChange, onPageSizeChange, pageSizeOptions = [5,10,20], disabled,
}: CompactPaginationProps) {
  const navBtnSx = { width: 26, height: 26, p: 0, '& .MuiSvgIcon-root': { fontSize: 18 } } as const;
  const handlePageSizeChange = (e: SelectChangeEvent) => {
    const v = Number(e.target.value);
    onPageSizeChange(v);
  };
  return (
    <Stack direction="row" justifyContent="flex-end" alignItems="center" spacing={2} sx={{ mt: 1 }}>
      <Stack direction="row" spacing={0.75} alignItems="center">
        <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>Rows per page:</Typography>
        <Select size="small" value={String(pageSize)} onChange={handlePageSizeChange} sx={{ height: 32, '& .MuiSelect-select': { py: 0.5 }, minWidth: 70 }} disabled={disabled}>
          {pageSizeOptions.map(n => <MenuItem key={n} value={String(n)}>{n}</MenuItem>)}
        </Select>
      </Stack>
      <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
        {rangeStart}-{rangeEnd} of {total}
      </Typography>
      <Stack direction="row" spacing={0.5} alignItems="center">
        <Tooltip title="Previous page">
          <span>
            <IconButton size="small" sx={navBtnSx} disabled={disabled || page <= 1} onClick={() => onPageChange(Math.max(1, page - 1))}>
              <ChevronLeftIcon />
            </IconButton>
          </span>
        </Tooltip>
        <Tooltip title="Next page">
          <span>
            <IconButton size="small" sx={navBtnSx} disabled={disabled || page >= pageCount || rangeEnd >= total} onClick={() => onPageChange(Math.min(pageCount, page + 1))}>
              <ChevronRightIcon />
            </IconButton>
          </span>
        </Tooltip>
      </Stack>
    </Stack>
  );
}
