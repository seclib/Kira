export const initialNodes = [
  {
    id: 'goal',
    type: 'custom',
    data: { label: 'Goal Node', status: 'pending' },
    position: { x: 0, y: 0 }
  },
  {
    id: 'planner',
    type: 'custom',
    data: { label: 'Planner Node', status: 'pending' },
    position: { x: 250, y: 0 }
  },
  {
    id: 'web',
    type: 'custom',
    data: { label: 'Web Tool Node', status: 'pending' },
    position: { x: 500, y: -80 }
  },
  {
    id: 'python',
    type: 'custom',
    data: { label: 'Python Node', status: 'pending' },
    position: { x: 500, y: 80 }
  },
  {
    id: 'memory',
    type: 'custom',
    data: { label: 'Memory Node', status: 'pending' },
    position: { x: 750, y: 0 }
  },
  {
    id: 'reflection',
    type: 'custom',
    data: { label: 'Reflection Node', status: 'pending' },
    position: { x: 1000, y: -40 }
  },
  {
    id: 'output',
    type: 'custom',
    data: { label: 'Output Node', status: 'pending' },
    position: { x: 1250, y: 0 }
  }
];

export const initialEdges = [
  { id: 'e1', source: 'goal', target: 'planner', animated: false },
  { id: 'e2', source: 'planner', target: 'web', animated: false },
  { id: 'e3', source: 'planner', target: 'python', animated: false },
  { id: 'e4', source: 'web', target: 'memory', animated: false },
  { id: 'e5', source: 'python', target: 'memory', animated: false },
  { id: 'e6', source: 'memory', target: 'reflection', animated: false },
  { id: 'e7', source: 'reflection', target: 'output', animated: false }
];
