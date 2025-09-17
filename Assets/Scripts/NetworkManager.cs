using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

namespace Lanbu.Network
{
    /// <summary>
    /// Main network manager for LAN discovery and connection
    /// </summary>
    public class NetworkManager : MonoBehaviour
    {
        [Header("Network Settings")]
        public int maxConnections = 8;
        public int serverPort = 7777;
        public string gameVersion = "0.53";
        
        [Header("Discovery Settings")]
        public int discoveryPort = 47777;
        public float discoveryInterval = 1.0f;
        
        private bool isServer = false;
        private bool isClient = false;
        private bool isDiscovering = false;
        
        void Start()
        {
            DontDestroyOnLoad(gameObject);
            Debug.Log($"Lanbu Network Manager initialized - Version {gameVersion}");
        }
        
        /// <summary>
        /// Start hosting a LAN game
        /// </summary>
        public void StartServer()
        {
            if (isServer || isClient) return;
            
            // Initialize server
            isServer = true;
            Debug.Log($"Starting LAN server on port {serverPort}");
            
            // Start discovery broadcast
            StartCoroutine(BroadcastServer());
        }
        
        /// <summary>
        /// Start looking for LAN games
        /// </summary>
        public void StartClient()
        {
            if (isServer || isClient) return;
            
            isClient = true;
            isDiscovering = true;
            Debug.Log("Starting LAN discovery...");
            
            StartCoroutine(DiscoverServers());
        }
        
        /// <summary>
        /// Stop all networking
        /// </summary>
        public void StopNetworking()
        {
            isServer = false;
            isClient = false;
            isDiscovering = false;
            
            StopAllCoroutines();
            Debug.Log("Network stopped");
        }
        
        private IEnumerator BroadcastServer()
        {
            while (isServer)
            {
                // Broadcast server availability
                string broadcastData = $"LANBU_SERVER:{gameVersion}:{serverPort}";
                Debug.Log($"Broadcasting: {broadcastData}");
                
                yield return new WaitForSeconds(discoveryInterval);
            }
        }
        
        private IEnumerator DiscoverServers()
        {
            while (isDiscovering)
            {
                // Listen for server broadcasts
                Debug.Log("Scanning for LAN servers...");
                
                yield return new WaitForSeconds(discoveryInterval);
            }
        }
        
        /// <summary>
        /// Connect to a discovered server
        /// </summary>
        /// <param name="serverIP">Server IP address</param>
        /// <param name="serverPort">Server port</param>
        public void ConnectToServer(string serverIP, int serverPort)
        {
            if (isServer) return;
            
            Debug.Log($"Connecting to server: {serverIP}:{serverPort}");
            // Connection logic here
        }
        
        void OnGUI()
        {
            GUI.Label(new Rect(10, 10, 200, 20), $"Lanbu Network v{gameVersion}");
            
            if (!isServer && !isClient)
            {
                if (GUI.Button(new Rect(10, 40, 100, 30), "Host Game"))
                {
                    StartServer();
                }
                
                if (GUI.Button(new Rect(120, 40, 100, 30), "Join Game"))
                {
                    StartClient();
                }
            }
            else
            {
                if (GUI.Button(new Rect(10, 40, 100, 30), "Stop"))
                {
                    StopNetworking();
                }
                
                if (isServer)
                {
                    GUI.Label(new Rect(10, 80, 200, 20), "Hosting LAN game...");
                }
                else if (isClient)
                {
                    GUI.Label(new Rect(10, 80, 200, 20), "Searching for games...");
                }
            }
        }
    }
}