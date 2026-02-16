import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Calendar, ArrowRight } from 'lucide-react';

const ScheduleStep: React.FC = () => {
    const { schedule, isLoading, error, schedule_time } = useWorkflowStore();
    const [date, setDate] = useState(schedule_time || "");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!date) return;
        await schedule(date);
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl mt-10 transition-colors">
            <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white flex items-center gap-2">
                <Calendar /> Schedule Post
            </h2>
            <p className="mb-4 text-gray-600 dark:text-gray-300">Select when you want to publish this content.</p>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Publish Date & Time</label>
                    <input
                        type="datetime-local"
                        className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        required
                    />
                </div>

                {error && (
                    <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-md text-sm">
                        {error}
                    </div>
                )}

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={isLoading || !date}
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                        Schedule & Continue <ArrowRight size={18} />
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ScheduleStep;
