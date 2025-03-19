import paramiko

def send_image_scp(image_path, remote_path, hostname, port, username, password):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the remote server
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # Use SCP to send the file
        with ssh.open_sftp() as sftp:
            sftp.put(image_path, remote_path)
        
        print(f"Image {image_path} successfully sent to {remote_path} on {hostname}")
    except Exception as e:
        print(f"Failed to send image: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    image_path = "/path/to/local/image.jpg"
    remote_path = "/path/to/remote/image.jpg"
    hostname = "example.com"
    port = 22
    username = "your_username"
    password = "your_password"

    send_image_scp(image_path, remote_path, hostname, port, username, password)