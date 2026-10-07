"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const data = [
  { name: "Nutrition (Macronutrients)", value: 50 },
  { name: "Ingredients (Quality, Additives)", value: 30 },
  { name: "Context (Processing level, NOVA)", value: 20 },
];

const COLORS = ["#FF6B6B", "#4ECDC4", "#FFE66D"];

export default function ScoreChart() {
  return (
    <div className="w-full bg-white rounded-3xl border-2 border-brand-border/30 shadow-sm p-6 flex flex-col items-center">
      <h3 className="font-bold text-xl text-brand-neutral mb-2 font-sans tracking-tight">Score Breakdown</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="45%"
              innerRadius={80}
              outerRadius={110}
              paddingAngle={3}
              dataKey="value"
              stroke="none"
              cornerRadius={6}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: "#fff", border: "none", borderRadius: "16px", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)", color: "#1a1a1a", fontSize: "14px", fontWeight: "bold", fontFamily: "inherit" }}
              itemStyle={{ color: "#1a1a1a" }}
            />
            <Legend wrapperStyle={{ fontSize: "14px", fontWeight: "bold", color: "#1a1a1a", fontFamily: "inherit" }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
