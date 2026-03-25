from subprocess import check_output

def run_command(command: str) -> str:
    return check_output(command, shell = True).decode("utf-8")