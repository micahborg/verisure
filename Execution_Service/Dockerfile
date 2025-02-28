# Use Node.js as the base image
FROM node:22.6

# Install Rust toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustc --version

# Install RISC Zero tools - modify the PATH to include the correct location
RUN curl -L https://risczero.com/install | bash
# Find out where rzup is installed and add that to PATH instead
ENV PATH="/root/.risc0/bin:${PATH}"
RUN ls -la /root/.risc0/bin || echo "Directory not found"
RUN which rzup || echo "rzup not found in PATH"

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy application files (including the Rust binary)
COPY . .

# Build the Rust binary
WORKDIR /usr/src/app/contracts_zk
RUN $HOME/.cargo/bin/cargo build --release

# Copy or move the built binary to the expected location
RUN cp /usr/src/app/contracts_zk/target/release/publisher /usr/src/app/src/utils/

# Ensure Rust binary has execute permissions
RUN chmod +x /usr/src/app/src/utils/publisher

# Expose the port your app uses
EXPOSE 8080

# Start the server
CMD ["node", "index.js"]
