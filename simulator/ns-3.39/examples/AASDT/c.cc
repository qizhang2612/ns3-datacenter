/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "iostream"

// Default Network Topology
//
//
//
//    point-to-point
//

/*Buffer Management Algorithms*/
# define DT 0
# define EDT 1
# define TDT 2
# define AASDT 3
# define ALPHA -2

/*switch port num*/
# define PORTNUM 8

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("experiment2");

void 
Gen_Congestion_UDP(uint16_t port,uint32_t portNum,NodeContainer& left,
                NodeContainer& right,Ipv4InterfaceContainer s[PORTNUM],double end_time){
  for(uint32_t i = 0;i < portNum;++i){
    UdpEchoServerHelper echoServer(port);
    ApplicationContainer serverApps = echoServer.Install(right.Get(i));
    serverApps.Start(Seconds(1.0));
    serverApps.Stop(Seconds(end_time));
    
    UdpEchoClientHelper echoClient(s[i].GetAddress(1), port++);
    echoClient.SetAttribute("MaxPackets", UintegerValue(100000));
    echoClient.SetAttribute("Interval", TimeValue(Seconds(0)));
    echoClient.SetAttribute("PacketSize", UintegerValue(1024));

    ApplicationContainer clientApps = echoClient.Install(left.Get(i));
    clientApps.Start(Seconds(2.0));
    clientApps.Stop(Seconds(end_time));
  }
                
}

void 
Gen_Congestion(uint16_t port,uint32_t portNum,NodeContainer& left,
                NodeContainer& right,uint32_t flowSize,double end_time){
  Time startApp = (NanoSeconds(150) + MilliSeconds(8000));
  for(uint32_t i = 0;i < portNum;++i){
    Ptr<Node> rxNode = right.Get(i);
    Ptr<Ipv4> ipv4 = rxNode->GetObject<Ipv4>();
    Ipv4InterfaceAddress rxInterface = ipv4->GetAddress(1, 0);
    Ipv4Address rxAddress = rxInterface.GetLocal();
    InetSocketAddress ad(rxAddress, port);
	  Address sinkAddress(ad);
    Ptr<BulkSendApplication> bulksend = CreateObject<BulkSendApplication>();
	  bulksend->SetAttribute("Protocol", TypeIdValue(TcpSocketFactory::GetTypeId()));
	  bulksend->SetAttribute("SendSize", UintegerValue(flowSize));
	  bulksend->SetAttribute("MaxBytes", UintegerValue(flowSize));
	  bulksend->SetAttribute("Remote", AddressValue(sinkAddress));
	  bulksend->SetStartTime(startApp);
	  bulksend->SetStopTime(Seconds(end_time));
    left.Get(i)->AddApplication(bulksend);

    PacketSinkHelper sink("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), port++));
	  ApplicationContainer sinkApp = sink.Install(right.Get(i));
	  sinkApp.Start(startApp);
	  sinkApp.Stop(Seconds(end_time));  
  }
                
}

int
main (int argc, char *argv[])
{
  CommandLine cmd (__FILE__);
  cmd.Parse (argc, argv);
  
  Time::SetResolution(Time::NS);
  //LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_INFO);
  //LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_INFO);

  uint32_t flowSize = 1800000;
  uint32_t BUFFERSIZE = 9*1000*1000;
  uint32_t LEFTNUM = PORTNUM;
  uint32_t RIGHTNUM = PORTNUM;
  double end_time = 30;

  NodeContainer leftNodes;
  leftNodes.Create(LEFTNUM);
  NodeContainer switchNodes;
  switchNodes.Create(PORTNUM);
  NodeContainer rightNodes;
  rightNodes.Create(RIGHTNUM);

  //int strategy = DT; 
  int strategy = EDT; 
  //int strategy = TDT; 
  //int strategy = AASDT; 

  // init ptr
  Ptr<UintegerValue> m_PortNumPtr = Create<UintegerValue>(PORTNUM);;
  Ptr<UintegerValue> m_usedBufferPtr = Create<UintegerValue>(0);
  Ptr<UintegerValue> m_stateChangePtr = Create<UintegerValue>(1);

  for(uint32_t i = 0;i < switchNodes.GetN();++i){
    Ptr<Node> node = switchNodes.Get(i);
    node->SetNodeType(1);
    node->m_switch->SetStrategy(strategy);
    node->m_switch->SetPort(i);
    //std::cout<<node->m_switch->GetPort()<<std::endl;
    node->m_switch->SetdtAlphaExp(ALPHA);
    node->m_switch->SetdtInitialAlphaExp(ALPHA);
    node->m_switch->SetSharedBufferSize(BUFFERSIZE);
    node->m_switch->SetUsedBufferPtr(m_usedBufferPtr);
    node->m_switch->SetPortNumPtr(m_PortNumPtr);
    node->m_switch->SetStateChangePtr(m_stateChangePtr);
  }

  if(strategy == DT){
    std::cout<<"--------- this is DT strategy ---------"<<std::endl;
  }else if(strategy == EDT){
    std::cout<<"--------- this is EDT strategy ---------"<<std::endl;
    //init ptr
    Ptr<UintegerValue> m_EDTCPortNumPtr = Create<UintegerValue>(PORTNUM);
    Ptr<UintegerValue> m_EDTNCPortNumPtr = Create<UintegerValue>(0);
    //init switch
    for(uint32_t i = 0;i < switchNodes.GetN();++i){
      Ptr<Node> node = switchNodes.Get(i);
      node->m_switch->SetEDTPortNumPtr(m_EDTCPortNumPtr,m_EDTNCPortNumPtr);
    }
  }else if(strategy == TDT){
    std::cout<<"--------- this is TDT strategy ---------"<<std::endl;
    //init ptr
    Ptr<UintegerValue> m_TDTNPortNumPtr = Create<UintegerValue>(PORTNUM);
    Ptr<UintegerValue> m_TDTAPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_TDTEPortNumPtr = Create<UintegerValue>(0);
    //init switch
    for(uint32_t i = 0;i < switchNodes.GetN();++i){
      Ptr<Node> node = switchNodes.Get(i);
      node->m_switch->SetTDTPortNumPtr(m_TDTNPortNumPtr,m_TDTAPortNumPtr,m_TDTEPortNumPtr);
    }
  }else if(strategy == AASDT){
    std::cout<<"--------- this is AASDT strategy ---------"<<std::endl;
    //init ptr
    Ptr<UintegerValue> m_AASDTNPortNumPtr = Create<UintegerValue>(PORTNUM);
    Ptr<UintegerValue> m_AASDTIPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCIPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCCPortNumPtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTITimePtr = Create<UintegerValue>(0);
    Ptr<UintegerValue> m_AASDTCTimePtr = Create<UintegerValue>(0);
    //init switch
    for(uint32_t i = 0;i < switchNodes.GetN();++i){
      Ptr<Node> node = switchNodes.Get(i);
      node->m_switch->SetAASDTPortNumPtr(m_AASDTNPortNumPtr,m_AASDTIPortNumPtr,m_AASDTCPortNumPtr,m_AASDTCIPortNumPtr,m_AASDTCCPortNumPtr);
      node->m_switch->SetAASDTICNumPtr(m_AASDTITimePtr,m_AASDTCTimePtr);
    }
    //Simulator::Schedule(Seconds(1), &(sw->m_switch->AASDTReset));
  }else{
    std::cout<<"--------- strategy error ---------"<<std::endl;
  }

  InternetStackHelper internet;
	Ipv4GlobalRoutingHelper globalRoutingHelper;
	internet.SetRoutingHelper(globalRoutingHelper);
  internet.Install(leftNodes);
  internet.Install(switchNodes);
  internet.Install(rightNodes);

  PointToPointHelper pointToPoint;
  Ipv4AddressHelper ipv4;
  Ipv4InterfaceContainer ls[LEFTNUM][PORTNUM];
  Ipv4InterfaceContainer sr[PORTNUM][RIGHTNUM];
  Ipv4InterfaceContainer s[PORTNUM];


  //l <--> s
  ipv4.SetBase("10.1.1.0", "255.255.255.0");
  pointToPoint.SetDeviceAttribute("DataRate", StringValue ("10Gbps"));
  pointToPoint.SetChannelAttribute("Delay", StringValue ("10ms"));
  //pointToPoint.SetQueue("ns3::DropTailQueue","MaxSize",QueueSizeValue(QueueSize(QueueSizeUnit::BYTES,2000)));
  for(uint32_t left = 0;left < LEFTNUM;++left){
    //ipv4.NewNetwork();
    NodeContainer nodeContainer = NodeContainer(leftNodes.Get(left), switchNodes.Get(left));
    NetDeviceContainer netDeviceContainer = pointToPoint.Install(nodeContainer);
    ls[left][left] = ipv4.Assign(netDeviceContainer);
  }

  //s <--> r
  ipv4.SetBase("10.2.1.0", "255.255.255.0");
  pointToPoint.SetDeviceAttribute("DataRate", StringValue ("1Gbps"));
  pointToPoint.SetChannelAttribute("Delay", StringValue ("10ms"));
  //pointToPoint.SetQueue("ns3::DropTailQueue","MaxSize",QueueSizeValue(QueueSize(QueueSizeUnit::BYTES,2000)));
  for(uint32_t right = 0;right < RIGHTNUM;++right){
    //ipv4.NewNetwork();
    NodeContainer nodeContainer = NodeContainer(switchNodes.Get(right),rightNodes.Get(right));
    NetDeviceContainer netDeviceContainer = pointToPoint.Install(nodeContainer);
    sr[right][right] = ipv4.Assign(netDeviceContainer);
    s[right] = sr[right][right];
  }

//---------------------------------TCP----------------------------------------
  
  uint32_t portNUM = 8;
  uint16_t port1 = 40000;
  uint16_t port2 = 50000;
  Gen_Congestion_UDP(port1,portNUM,leftNodes,rightNodes,s,end_time);
  Gen_Congestion(port2,portNUM,leftNodes,rightNodes,flowSize,end_time);
  

//----------------------------------------------------------------------------

  // Flow monitor
  Ptr<FlowMonitor> flowMonitor;
  FlowMonitorHelper flowHelper;
  flowMonitor = flowHelper.InstallAll();
  

  Ipv4GlobalRoutingHelper::PopulateRoutingTables();
  Simulator::Stop(Seconds(end_time));
  Simulator::Run();

  flowMonitor->SerializeToXmlFile("flow-monitor2.xml", true, true);
  Simulator::Destroy();
  return 0;
}
