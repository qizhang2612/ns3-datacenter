#ifndef AI_MMU_H
#define AI_MMU_H

#include "switch-mmu.h"
#include "ns3/nstime.h"


namespace ns3
{

class AiMmu : public SwitchMmu
{
  public:
    static TypeId GetTypeId(void);
    AiMmu(void);
    virtual ~AiMmu(void);
};












}

#endif