import tkinter as tk
from tkinter import ttk, messagebox

class RoundRobinScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin Scheduler")

        self.processes = []

        # Input Frame
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)

        tk.Label(self.input_frame, text="Process Name").grid(row=0, column=0)
        tk.Label(self.input_frame, text="Arrival Time").grid(row=0, column=1)
        tk.Label(self.input_frame, text="Priority").grid(row=0, column=2)
        tk.Label(self.input_frame, text="Burst Time").grid(row=0, column=3)

        self.process_name = tk.Entry(self.input_frame, width=15)
        self.process_name.grid(row=1, column=0)
        self.arrival_time = tk.Entry(self.input_frame, width=10)
        self.arrival_time.grid(row=1, column=1)
        self.priority = tk.Entry(self.input_frame, width=10)
        self.priority.grid(row=1, column=2)
        self.burst_time = tk.Entry(self.input_frame, width=10)
        self.burst_time.grid(row=1, column=3)

        tk.Button(self.input_frame, text="Add Process", command=self.add_process).grid(row=1, column=4, padx=5)

        # Quantum Input
        self.quantum_label = tk.Label(root, text="Time Quantum: ")
        self.quantum_label.pack()
        self.quantum_entry = tk.Entry(root, width=10)
        self.quantum_entry.pack()

        # Output Frame
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=10)

        self.table = ttk.Treeview(self.output_frame, columns=("name", "arrival_time", "priority", "burst_time", "completion_time", "turnaround_time", "waiting_time"), show="headings")
        self.table.heading("name", text="Name")
        self.table.heading("arrival_time", text="Arrival Time")
        self.table.heading("priority", text="Priority")
        self.table.heading("burst_time", text="Burst Time")
        self.table.heading("completion_time", text="Completion Time")
        self.table.heading("turnaround_time", text="Turnaround Time")
        self.table.heading("waiting_time", text="Waiting Time")
        self.table.pack()

        # Gantt Chart Frame
        self.gantt_chart_frame = tk.Frame(root)
        self.gantt_chart_frame.pack(pady=10)

        # Buttons
        tk.Button(root, text="Run Scheduler", command=self.run_scheduler).pack(pady=5)
        tk.Button(root, text="Clear All", command=self.clear_all).pack(pady=5)

    def add_process(self):
        name = self.process_name.get()
        arrival = self.arrival_time.get()
        priority = self.priority.get()
        burst = self.burst_time.get()

        if not name or not arrival or not priority or not burst:
            messagebox.showerror("Input Error", "All fields must be filled!")
            return

        try:
            arrival = int(arrival)
            priority = int(priority)
            burst = int(burst)
        except ValueError:
            messagebox.showerror("Input Error", "Arrival Time, Priority, and Burst Time must be integers!")
            return

        self.processes.append({
            "name": name,
            "arrival_time": arrival,
            "priority": priority,
            "burst_time": burst,
            "remaining_time": burst
        })

        messagebox.showinfo("Success", f"Process {name} added successfully!")
        self.process_name.delete(0, tk.END)
        self.arrival_time.delete(0, tk.END)
        self.priority.delete(0, tk.END)
        self.burst_time.delete(0, tk.END)

    def run_scheduler(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes to schedule!")
            return

        try:
            quantum = int(self.quantum_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Quantum must be an integer!")
            return

        processes = sorted(self.processes, key=lambda x: x['arrival_time'])

        time = 0
        gantt_chart = []
        ready_queue = []

        while any(p['remaining_time'] > 0 for p in processes):
            for process in processes:
                if process['arrival_time'] <= time and process['remaining_time'] > 0 and process not in ready_queue:
                    ready_queue.append(process)

            if ready_queue:
                current_process = ready_queue.pop(0)
                execution_time = min(quantum, current_process['remaining_time'])

                gantt_chart.append((time, time + execution_time, current_process['name']))
                current_process['remaining_time'] -= execution_time
                time += execution_time

                if current_process['remaining_time'] > 0:
                    ready_queue.append(current_process)
                else:
                    current_process['completion_time'] = time
            else:
                time += 1

        for process in processes:
            process['turnaround_time'] = process['completion_time'] - process['arrival_time']
            process['waiting_time'] = process['turnaround_time'] - process['burst_time']

        self.update_table(processes)
        self.display_gantt_chart(gantt_chart)

    def update_table(self, processes):
        for row in self.table.get_children():
            self.table.delete(row)

        for process in processes:
            self.table.insert("", "end", values=(
                process['name'],
                process['arrival_time'],
                process['priority'],
                process['burst_time'],
                process.get('completion_time', 0),
                process.get('turnaround_time', 0),
                process.get('waiting_time', 0)
            ))

    def display_gantt_chart(self, gantt_chart):
        for widget in self.gantt_chart_frame.winfo_children():
            widget.destroy()

        gantt_text = ""
        for start, end, process in gantt_chart:
            gantt_text += f"| {process} ({start}-{end}) "
        gantt_text += "|"

        tk.Label(self.gantt_chart_frame, text="Gantt Chart:").pack()
        tk.Label(self.gantt_chart_frame, text=gantt_text, font=("Courier", 12)).pack()

    def clear_all(self):
        self.processes = []
        self.quantum_entry.delete(0, tk.END)
        for row in self.table.get_children():
            self.table.delete(row)
        for widget in self.gantt_chart_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RoundRobinScheduler(root)
    root.mainloop()
