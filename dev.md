open webui 标准开发逻辑
1.Prerequisites:Operating System: An operating system
a.Python: 3.11 or higher (e.g., 3.11.x)
b.Node.js: 22.10 or higher
c.IDE: VSCode (recommended, used for this setup)
d.Conda (recommended for backend environment)
2.Clone the Repository:Open a terminal (e.g., VSCode integrated terminal).
a.Navigate to your desired directory.
b.Run:git clone https://github.com/open-webui/open-webui.git
cd open-webui
3.Frontend Setup:Copy the example environment file:cp -RPp .env.example .env
a.(No custom changes made to .env for reproduction, default settings are used.)
b.Install frontend dependencies (from open-webui directory):npm install
c.Start the frontend development server (from open-webui directory):npm run dev
d.Open your web browser and navigate to http://localhost:5173. You should see the frontend waiting for the backend. Keep this terminal running.
4.Backend Setup:Open a new terminal instance (e.g., VSCode's "Terminal > New Terminal").
a.Navigate to the backend directory in this new terminal:cd backend
b.Create and activate a Conda environment:conda create --name open-webui python=3.11
conda activate open-webui
c.Install backend dependencies (with Conda environment activated, from backend directory):pip install -r requirements.txt -U
d.Start the backend development server (from backend directory):sh dev.sh
e.Wait for the backend server to start successfully.


npm run dev

conda activate open-webui

cd backend
sh dev.sh

docker-command.md