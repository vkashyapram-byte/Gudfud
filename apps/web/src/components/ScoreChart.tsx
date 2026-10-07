"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const data = [
  { name: "Nutrition (Macronutrients)", value: 50 },
  { name: "Ingredients (Quality, Additives)", value: 30 },
  { name: "Context (Processing level, NOVA)", value: 20 },
];

const COLORS = ["#1a1a1a", "#666666", "#e5e5e5"];

export default function ScoreChart() {
  return (
    <div className="w-full h-80 bg-white border border-brand-border p-4 flex flex-col items-center">
      <h3 className="uppercase font-bold text-brand-neutral mb-2">Score Breakdown</h3>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #1a1a1a", borderRadius: "0", color: "#1a1a1a", textTransform: "uppercase", fontSize: "12px", fontWeight: "bold" }}
            itemStyle={{ color: "#1a1a1a" }}
          />
          <Legend wrapperStyle={{ fontSize: "12px", textTransform: "uppercase", fontWeight: "bold", color: "#1a1a1a" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
