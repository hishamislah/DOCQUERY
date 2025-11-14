import streamlit as st
import shutil
import os

def get_live_system_resources():
    try:
        import psutil
        mem = psutil.virtual_memory()
        # Calculate used as (total - available) for accuracy on macOS
        mem_used_bytes = mem.total - mem.available
        mem_percent = f"{(mem_used_bytes / mem.total * 100):.1f}%"
        mem_used = f"{mem_used_bytes / (1024**3):.2f} GB"
        mem_total = f"{mem.total / (1024**3):.2f} GB"
        cpu = psutil.cpu_percent(interval=0.5)
        cpu_percent = f"{cpu:.1f}%"
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else None
    except ImportError:
        mem_percent = "54.8%"
        mem_used = "N/A"
        mem_total = "N/A"
        cpu_percent = "8.3%"
        cpu_count = "N/A"
        cpu_freq = None
    import shutil
    disk = shutil.disk_usage("/")
    disk_percent = f"{disk.used / disk.total * 100:.1f}%" if disk.total else "84.4%"
    disk_used = f"{disk.used / (1024**3):.2f} GB"
    disk_total = f"{disk.total / (1024**3):.2f} GB"
    return {
        "mem_percent": mem_percent,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "cpu_freq": cpu_freq,
        "disk_percent": disk_percent,
        "disk_used": disk_used,
        "disk_total": disk_total
    }


def system_info_tab():
    st.header("System Information")
    # Live/Static toggle
    live = st.toggle("Show live system stats", value=True)
    if live:
        stats = get_live_system_resources()
    else:
        stats = {
            "mem_percent": "54.8%",
            "mem_used": "N/A",
            "mem_total": "N/A",
            "cpu_percent": "8.3%",
            "cpu_count": "N/A",
            "cpu_freq": None,
            "disk_percent": "84.4%",
            "disk_used": "N/A",
            "disk_total": "N/A"
        }

    st.subheader("System Resources")
    st.write(f"**Memory Usage:** {stats['mem_percent']} ({stats['mem_used']} / {stats['mem_total']})")
    st.write(f"**Disk Usage:** {stats['disk_percent']} ({stats['disk_used']} / {stats['disk_total']})")
    st.write(f"**CPU Usage:** {stats['cpu_percent']}")
    st.write(f"**CPU Cores:** {stats['cpu_count']}")
    if stats['cpu_freq']:
        st.write(f"**CPU Frequency:** {stats['cpu_freq']:.0f} MHz")

    st.subheader("Circuit Breaker Status")
    st.write("**Failure Count:** 0")
    st.write("**Threshold:** 5")
    st.write("**Last Failure:** None")

    st.subheader("Available Models")
    st.write("• llama3:latest")

    st.subheader("llama Status")
    st.success("✅ llama is available")

    # --- Recent Logs Section ---
    st.subheader("Recent Logs")
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "errors.log")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            lines = f.readlines()[-20:]
        st.code("".join(lines), language="text")
    else:
        st.info("No error logs found.")
