package com.glowbeast.lanbu

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import kotlinx.coroutines.*
import java.net.*

/**
 * Background service for LAN discovery and networking
 */
class NetworkService : Service() {
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.IO + serviceJob)
    private var isDiscovering = false
    
    companion object {
        private const val TAG = "NetworkService"
        private const val DISCOVERY_PORT = 47777
        private const val BROADCAST_INTERVAL = 2000L
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Network service created")
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            "START_DISCOVERY" -> startDiscovery()
            "STOP_DISCOVERY" -> stopDiscovery()
            "START_BROADCAST" -> startBroadcast()
        }
        return START_STICKY
    }
    
    private fun startDiscovery() {
        if (isDiscovering) return
        
        isDiscovering = true
        Log.d(TAG, "Starting LAN discovery")
        
        serviceScope.launch {
            try {
                val socket = DatagramSocket(DISCOVERY_PORT)
                socket.broadcast = true
                socket.soTimeout = 1000
                
                while (isDiscovering) {
                    try {
                        val buffer = ByteArray(1024)
                        val packet = DatagramPacket(buffer, buffer.size)
                        socket.receive(packet)
                        
                        val message = String(packet.data, 0, packet.length)
                        if (message.startsWith("LANBU_SERVER:")) {
                            handleServerDiscovered(packet.address.hostAddress, message)
                        }
                    } catch (e: SocketTimeoutException) {
                        // Continue listening
                    }
                    
                    delay(100)
                }
                
                socket.close()
            } catch (e: Exception) {
                Log.e(TAG, "Discovery error: ${e.message}")
            }
        }
    }
    
    private fun startBroadcast() {
        Log.d(TAG, "Starting server broadcast")
        
        serviceScope.launch {
            try {
                val socket = DatagramSocket()
                socket.broadcast = true
                
                val message = "LANBU_SERVER:0.53:7777"
                val data = message.toByteArray()
                
                while (isActive) {
                    try {
                        val packet = DatagramPacket(
                            data, data.size,
                            InetAddress.getByName("255.255.255.255"),
                            DISCOVERY_PORT
                        )
                        socket.send(packet)
                        Log.d(TAG, "Broadcast sent: $message")
                    } catch (e: Exception) {
                        Log.e(TAG, "Broadcast error: ${e.message}")
                    }
                    
                    delay(BROADCAST_INTERVAL)
                }
                
                socket.close()
            } catch (e: Exception) {
                Log.e(TAG, "Broadcast setup error: ${e.message}")
            }
        }
    }
    
    private fun stopDiscovery() {
        isDiscovering = false
        Log.d(TAG, "Stopping discovery")
    }
    
    private fun handleServerDiscovered(ip: String?, message: String) {
        Log.d(TAG, "Server discovered: $ip - $message")
        
        // Send broadcast to Unity
        val intent = Intent("com.glowbeast.lanbu.SERVER_DISCOVERED").apply {
            putExtra("server_ip", ip)
            putExtra("server_info", message)
        }
        sendBroadcast(intent)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        isDiscovering = false
        serviceJob.cancel()
        Log.d(TAG, "Network service destroyed")
    }
}