// Actividad Integradora 1
// Mayra Fernanda Camacho Rodríguez	A01378998
// Víctor Martínez Román			A01746361
// Melissa Aurora Fadanelli Ordaz		A01749483
// Juan Pablo Castañeda Serrano		A01752030
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class model : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    string getAgents = "/getRobots";
    string getBoxes = "/getBoxes";
    string getShelves = "/getShelves";
    string sendConfig = "/init";
    string update = "/update";
    AgentsData agentsData, boxData, shelvesData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, GameObject> boxes;
    Dictionary<string, GameObject> shelves;
    Dictionary<string, Vector3> prevPositions, currPositions;
    Dictionary<string, Vector3> pPosBox, cPosBox;
    Dictionary<string, Vector3> pPosSh, cPosSh;

    bool updated, started, upBox, stBox = false;

    public GameObject agentPrefab, boxPrefab, shelvePrefab, floor;
    public int box, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        boxData = new AgentsData();
        shelvesData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();
        pPosBox = new Dictionary<string, Vector3>();
        cPosBox = new Dictionary<string, Vector3>();
        pPosSh = new Dictionary<string, Vector3>();
        cPosSh = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        boxes = new Dictionary<string, GameObject>();
        shelves = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
        if (upBox)
        {
            foreach(var box in cPosBox)
            {
                Vector3 currentPositionBox = box.Value;
                Vector3 previousPositionBox = pPosBox[box.Key];

                Vector3 interpolated = Vector3.Lerp(previousPositionBox, currentPositionBox, dt);
                Vector3 direction = currentPositionBox - interpolated;

                boxes[box.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) boxes[box.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + update);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetBoxData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("box", box.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfig, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetBoxData());
            StartCoroutine(GetShelvesData());
        }
    }

    IEnumerator GetAgentsData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgents);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);

                    if(!started)
                    {
                        prevPositions[agent.id] = newAgentPosition;
                        agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity);
                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();
                        if(currPositions.TryGetValue(agent.id, out currentPosition))
                            prevPositions[agent.id] = currentPosition;
                        currPositions[agent.id] = newAgentPosition;
                    }
            }

            updated = true;
            if(!started) started = true;
        }
    }

    IEnumerator GetBoxData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxes);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            boxData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData box in boxData.positions)
            {
                Vector3 newBoxPosition = new Vector3(box.x, box.y, box.z);

                  if(!stBox)
                  {
                      pPosBox[box.id] = newBoxPosition;
                      boxes[box.id] = Instantiate(boxPrefab, newBoxPosition, Quaternion.identity);
                  }
                  else
                  {
                      Vector3 currentPositionObs = new Vector3();
                      if(cPosBox.TryGetValue(box.id, out currentPositionObs))
                          pPosBox[box.id] = currentPositionObs;
                      cPosBox[box.id] = newBoxPosition;
                  }
            }

            upBox = true;
            if(!stBox) stBox = true;
        }
    }

    IEnumerator GetShelvesData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getShelves);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            shelvesData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData shelve in shelvesData.positions)
            {
                Instantiate(shelvePrefab, new Vector3(shelve.x, shelve.y, shelve.z), Quaternion.identity);
            }
        }
    }
}
