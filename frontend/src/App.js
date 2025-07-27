import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [reports, setReports] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form states
  const [crimeForm, setCrimeForm] = useState({
    crime_type: "",
    area: "",
    location: "",
    description: "",
    reported_by: "Anonymous"
  });

  const crimeTypes = [
    "Theft", "Burglary", "Assault", "Vandalism", "Fraud", 
    "Drug-related", "Vehicle Crime", "Cybercrime", "Domestic Violence", "Other"
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [reportsRes, statsRes, predictionsRes] = await Promise.all([
        axios.get(`${API}/reports?limit=10`),
        axios.get(`${API}/stats`),
        axios.get(`${API}/predictions?limit=5`)
      ]);
      
      setReports(reportsRes.data);
      setStats(statsRes.data);
      setPredictions(predictionsRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const submitCrimeReport = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/reports`, crimeForm);
      alert("Crime report submitted successfully!");
      setCrimeForm({
        crime_type: "",
        area: "",
        location: "",
        description: "",
        reported_by: "Anonymous"
      });
      fetchData();
    } catch (error) {
      alert("Error submitting report: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const generatePrediction = async (area = "") => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/predict`, { area: area || null });
      alert("Prediction generated successfully!");
      fetchData();
    } catch (error) {
      alert("Error generating prediction: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const Dashboard = () => (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold">Total Reports</h3>
          <p className="text-3xl font-bold">{stats?.total_reports || 0}</p>
        </div>
        
        <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold">Areas Covered</h3>
          <p className="text-3xl font-bold">{stats?.by_area?.length || 0}</p>
        </div>
        
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold">Predictions Made</h3>
          <p className="text-3xl font-bold">{predictions.length}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Crime Reports by Area</h3>
          <div className="space-y-3">
            {stats?.by_area?.slice(0, 5).map((item, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{item.area}</span>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                  {item.count} reports
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Crime Types</h3>
          <div className="space-y-3">
            {stats?.by_type?.slice(0, 5).map((item, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{item.type}</span>
                <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                  {item.count} cases
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gray-800">Recent Reports</h3>
          <button
            onClick={() => setActiveTab("reports")}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            View All →
          </button>
        </div>
        <div className="space-y-3">
          {reports.slice(0, 3).map((report) => (
            <div key={report.id} className="border-l-4 border-blue-500 pl-4 py-2">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-gray-800">{report.crime_type}</h4>
                  <p className="text-gray-600">{report.area} - {report.location}</p>
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(report.timestamp).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ReportForm = () => (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Submit Crime Report</h2>
        
        <form onSubmit={submitCrimeReport} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Crime Type *
            </label>
            <select
              value={crimeForm.crime_type}
              onChange={(e) => setCrimeForm({...crimeForm, crime_type: e.target.value})}
              required
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select crime type</option>
              {crimeTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Area/Neighborhood *
            </label>
            <input
              type="text"
              value={crimeForm.area}
              onChange={(e) => setCrimeForm({...crimeForm, area: e.target.value})}
              required
              placeholder="e.g., Downtown, Park Avenue, etc."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specific Location *
            </label>
            <input
              type="text"
              value={crimeForm.location}
              onChange={(e) => setCrimeForm({...crimeForm, location: e.target.value})}
              required
              placeholder="e.g., 123 Main St, Central Park, etc."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              value={crimeForm.description}
              onChange={(e) => setCrimeForm({...crimeForm, description: e.target.value})}
              required
              rows="4"
              placeholder="Provide details about the incident..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reported By (Optional)
            </label>
            <input
              type="text"
              value={crimeForm.reported_by}
              onChange={(e) => setCrimeForm({...crimeForm, reported_by: e.target.value})}
              placeholder="Anonymous"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? "Submitting..." : "Submit Report"}
          </button>
        </form>
      </div>
    </div>
  );

  const ReportsView = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">All Crime Reports</h2>
        <button
          onClick={fetchData}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-6">
        {reports.map((report) => (
          <div key={report.id} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-800">{report.crime_type}</h3>
                <p className="text-gray-600">{report.area} - {report.location}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">
                  {new Date(report.timestamp).toLocaleString()}
                </p>
                <p className="text-sm text-gray-500">By: {report.reported_by}</p>
              </div>
            </div>
            <p className="text-gray-700">{report.description}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const PredictionsView = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">AI Crime Predictions</h2>
        <div className="space-x-2">
          <button
            onClick={() => generatePrediction()}
            disabled={loading}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? "Generating..." : "Generate Overall Prediction"}
          </button>
        </div>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
        <p className="text-blue-800">
          <strong>How it works:</strong> Our AI analyzes recent crime data to identify patterns, 
          predict potential hotspots, and provide safety recommendations for different areas.
        </p>
      </div>

      <div className="grid gap-6">
        {predictions.map((prediction) => (
          <div key={prediction.id} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-800">
                  {prediction.area ? `Analysis for ${prediction.area}` : "General Crime Analysis"}
                </h3>
                <div className="flex space-x-2 mt-2">
                  {prediction.insights.map((insight, index) => (
                    <span
                      key={index}
                      className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs"
                    >
                      {insight}
                    </span>
                  ))}
                </div>
              </div>
              <div className="text-right">
                <span className={`px-3 py-1 rounded-full text-sm ${
                  prediction.confidence === 'High' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {prediction.confidence} Confidence
                </span>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(prediction.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                {prediction.prediction_text}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🚔 Crime Reporting Portal
              </h1>
              <p className="text-gray-600">Community Safety Through Data & AI</p>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: "dashboard", label: "Dashboard", icon: "📊" },
              { id: "report", label: "Report Crime", icon: "📝" },
              { id: "reports", label: "View Reports", icon: "📋" },
              { id: "predictions", label: "AI Predictions", icon: "🔮" }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "report" && <ReportForm />}
        {activeTab === "reports" && <ReportsView />}
        {activeTab === "predictions" && <PredictionsView />}
      </main>
    </div>
  );
};

export default App;