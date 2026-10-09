/**
 * Crisis Timeline Chart Component
 * Displays crisis events over time
 */

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { LoadingState } from '../Common/TableComponents';

interface CrisisTimelineChartProps {
  data: any[];
  isLoading?: boolean;
}

function CrisisTimelineChart({ data = [], isLoading = false }: CrisisTimelineChartProps) {
  if (isLoading) {
    return <LoadingState message="Loading timeline..." />;
  }

  if (data.length === 0) {
    return (
      <div className="card h-full">
        <div className="card-header">
          <h2 className="card-title">Crisis Timeline</h2>
        </div>
        <div className="flex items-center justify-center py-12">
          <p className="text-gray-500">No data available</p>
        </div>
      </div>
    );
  }

  // Transform data for the chart
  const chartData = data.map((item, index) => ({
    name: item.date || item.created_at || `Day ${index + 1}`,
    crises: item.count || item.value || 0,
  }));

  return (
    <div className="card h-full">
      <div className="card-header">
        <h2 className="card-title">Crisis Timeline</h2>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="name" 
              stroke="#6b7280" 
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis stroke="#6b7280" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="crises"
              stroke="#3b82f6"
              strokeWidth={3}
              activeDot={{ r: 8, fill: '#3b82f6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default CrisisTimelineChart;
