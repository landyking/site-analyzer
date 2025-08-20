
import type { MapTaskDetails } from '../../client/types.gen';

interface ProgressTabProps {
	mapTask?: MapTaskDetails | null;
}


const ProgressTab: React.FC<ProgressTabProps> = ({ mapTask }) => (
	<pre style={{ fontSize: 12, background: '#f5f5f5', padding: 12, borderRadius: 4, overflowX: 'auto' }}>
		{JSON.stringify(mapTask, null, 2)}
	</pre>
);

export default ProgressTab;
