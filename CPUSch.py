import tkinter as tk
from tkinter import messagebox

# Shortest Job Next (SJN) Scheduling
def sjn(processes, gantt_table):
    processes.sort(key=lambda x: x[1])  # Sort by burst time (Shortest Job First)
    return fcfs(processes, gantt_table)

# Shortest Remaining Time (SRT) Scheduling
def srt(processes, time_quantum, gantt_table):
    current_time = 0
    gantt_data = []
    processes = [(pid, burst_time, burst_time) for pid, burst_time in processes]  # Initialize remaining times
    remaining_processes = processes[:]
    while remaining_processes:
        remaining_processes.sort(key=lambda x: x[2])  # Sort by remaining time (Shortest Remaining Time)
        process_id, remaining_time, burst_time = remaining_processes.pop(0)
        
        execution_time = min(remaining_time, time_quantum)
        gantt_data.append((process_id, current_time, current_time + execution_time))
        current_time += execution_time
        remaining_time -= execution_time

        if remaining_time > 0:
            remaining_processes.append((process_id, remaining_time, burst_time))  # Re-add process with updated remaining time
        else:
            gantt_data.append((process_id, current_time, current_time))

    display_gantt_chart(gantt_data, gantt_table)
    return calculate_wait_turnaround_times(gantt_data)

# First Come First Serve (FCFS) Scheduling
def fcfs(processes, gantt_table):
    current_time = 0
    gantt_data = []
    
    # FCFS just executes processes in the order they arrive
    for process_id, burst_time, _ in processes:
        gantt_data.append((process_id, current_time, current_time + burst_time))
        current_time += burst_time
    
    display_gantt_chart(gantt_data, gantt_table)
    return calculate_wait_turnaround_times(gantt_data)

# Calculate Waiting and Turnaround Times
def calculate_wait_turnaround_times(gantt_data):
    waiting_times = {}
    turnaround_times = {}
    process_completion_time = {}

    for process_id, start_time, end_time in gantt_data:
        process_completion_time[process_id] = end_time
        turnaround_times[process_id] = end_time - start_time
        waiting_times[process_id] = end_time - (process_completion_time.get(process_id, 0) - turnaround_times.get(process_id, 0))
    
    return waiting_times, turnaround_times

# Display Gantt Chart
def display_gantt_chart(gantt_data, gantt_table):
    for widget in gantt_table.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(gantt_table, height=50, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)

    x_offset = 10
    y_offset = 20
    box_width = 50
    box_height = 30

    for process_id, start_time, end_time in gantt_data:
        canvas.create_rectangle(x_offset, y_offset, x_offset + box_width, y_offset + box_height, outline="black", fill="lightblue")
        canvas.create_text(x_offset + box_width / 2, y_offset + box_height / 2, text=f"P{process_id}")
        x_offset += box_width

# Print Results (Waiting & Turnaround Times)
def print_results(waiting_times, turnaround_times, num_processes, output_text):
    output_text.insert(tk.END, "\nProcess\tBurst Time\tWaiting Time\tTurnaround Time\n")
    total_waiting_time = 0
    total_turnaround_time = 0

    for process_id in sorted(waiting_times):
        waiting_time = waiting_times[process_id]
        turnaround_time = turnaround_times[process_id]
        burst_time = turnaround_time - waiting_time
        total_waiting_time += waiting_time
        total_turnaround_time += turnaround_time

        output_text.insert(tk.END, f"{process_id}\t\t{burst_time}\t\t{waiting_time}\t\t{turnaround_time}\n")

    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes
    output_text.insert(tk.END, f"\nAverage Waiting Time: {avg_waiting_time:.2f}\n")
    output_text.insert(tk.END, f"Average Turnaround Time: {avg_turnaround_time:.2f}\n")

# Start the selected scheduling algorithm
def start_scheduling():
    try:
        n = int(num_processes_entry.get())
        processes = []

        for i in range(1, n + 1):
            burst_time = int(process_burst_entries[i - 1].get())
            processes.append((i, burst_time, burst_time))  # (process_id, remaining_time, burst_time)

        output_text.delete(1.0, tk.END)
        algorithm = algorithm_var.get()

        if algorithm == "Round Robin":
            time_quantum = int(time_quantum_entry.get())  # Ensure time quantum is provided
            if time_quantum <= 0:
                messagebox.showerror("Input Error", "Time Quantum must be greater than 0 for Round Robin.")
                return
            waiting_times, turnaround_times = round_robin(processes, time_quantum, gantt_table)
        elif algorithm == "Shortest Job Next (SJN)":
            waiting_times, turnaround_times = sjn(processes, gantt_table)
        elif algorithm == "Shortest Remaining Time (SRT)":
            time_quantum = int(time_quantum_entry.get())  # Time quantum is also required for SRT
            if time_quantum <= 0:
                messagebox.showerror("Input Error", "Time Quantum must be greater than 0 for Shortest Remaining Time.")
                return
            waiting_times, turnaround_times = srt(processes, time_quantum, gantt_table)
        elif algorithm == "First Come First Serve (FCFS)":
            waiting_times, turnaround_times = fcfs(processes, gantt_table)

        print_results(waiting_times, turnaround_times, n, output_text)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")

# Create process burst time entries
def create_process_entries():
    try:
        n = int(num_processes_entry.get())
        for widget in process_frame.winfo_children():
            widget.destroy()

        global process_burst_entries
        process_burst_entries = []

        for i in range(n):
            tk.Label(process_frame, text=f"Burst Time for Process {i + 1}:").grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(process_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            process_burst_entries.append(entry)

        # If Round Robin is selected, show the time quantum input
        if algorithm_var.get() == "Round Robin" or algorithm_var.get() == "Shortest Remaining Time (SRT)":
            time_quantum_label.grid(row=3, column=0, padx=5, pady=5)
            time_quantum_entry.grid(row=3, column=1, padx=5, pady=5)
        else:
            time_quantum_label.grid_forget()
            time_quantum_entry.grid_forget()

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of processes.")

# Create the main application window
root = tk.Tk()
root.title("Process Scheduling")

# Input for number of processes
tk.Label(root, text="Number of Processes:").grid(row=0, column=0, padx=5, pady=5)
num_processes_entry = tk.Entry(root)
num_processes_entry.grid(row=0, column=1, padx=5, pady=5)

# Dropdown for scheduling algorithm selection
tk.Label(root, text="Select Algorithm:").grid(row=1, column=0, padx=5, pady=5)
algorithm_var = tk.StringVar(value="Round Robin")
algorithm_menu = tk.OptionMenu(root, algorithm_var, "Round Robin", "Shortest Job Next (SJN)", "Shortest Remaining Time (SRT)", "First Come First Serve (FCFS)")
algorithm_menu.grid(row=1, column=1, padx=5, pady=5)

# Time Quantum field (hidden by default)
time_quantum_label = tk.Label(root, text="Time Quantum:")
time_quantum_entry = tk.Entry(root)

# Time Quantum field should appear below algorithm selection, before the Generate button
time_quantum_label.grid(row=2, column=0, padx=5, pady=5)
time_quantum_entry.grid(row=2, column=1, padx=5, pady=5)

# Button to generate process entries
generate_button = tk.Button(root, text="Generate Processes", command=create_process_entries)
generate_button.grid(row=3, column=0, columnspan=2, pady=10)

# Frame to hold process burst time entries
process_frame = tk.Frame(root)
process_frame.grid(row=4, column=0, columnspan=2)

# Button to start scheduling
start_button = tk.Button(root, text="Start Scheduling", command=start_scheduling)
start_button.grid(row=5, column=0, columnspan=2, pady=10)

# Frame to display Gantt chart
gantt_table = tk.Frame(root)
gantt_table.grid(row=6, column=0, columnspan=2, pady=10)

# Output text area
output_text = tk.Text(root, height=15, width=50)
output_text.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Start the GUI loop
root.mainloop()
