# decode된 opcode와 주소를 사람이 읽기 쉬운 메모리 참조 instruction 문자열로 변환
def choise_instruction_name(opcode, reg_AR) -> str:
    # instuction name 정하기
    if opcode == 0:
        cur_instruction_name = f'AND {reg_AR:03X}'
    elif opcode == 1:
        cur_instruction_name = f'ADD {reg_AR:03X}'
    elif opcode == 2:
        cur_instruction_name = f'LDA {reg_AR:03X}'
    elif opcode == 3:
        cur_instruction_name = f'STA {reg_AR:03X}'
    elif opcode == 4:
        cur_instruction_name = f'BUN {reg_AR:03X}'
    elif opcode == 5:
        cur_instruction_name = f'BSA {reg_AR:03X}'
    elif opcode == 6:
        cur_instruction_name = f'ISZ {reg_AR:03X}'
        
    
    return cur_instruction_name

def final_register(reg):
    print("\n============= final register =============\n")
    
    print(f'PC = {reg["PC"]:03X}')
    print(f'AR = {reg["AR"]:03X}')
    print(f'IR = {reg["IR"]:04X}')
    print(f'DR = {reg["DR"]:04X}')
    print(f'AC = {reg["AC"]:04X}')
    print(f'I = {reg["I"]}')
    print(f'SC = {reg["SC"]}')
    print(f'E = {reg["E"]}')
    print(f'S = {reg["S"]}')
    
def final_memory(M):
    print("\n============= final memory =============\n")
    for addr in range(0x000, 0x007):
        print(f'M[{addr:03X}] = {M[addr]:04X}')
    

def simulate_cycle():
    ## 레지스터, 메모리 선언
    # 메모리 선언
    M = [0] * 0x100        
    M[0x000] = 0x2004    # LDA 004 / Load first operand into AC
    M[0x001] = 0x1005    # ADD 005 / Add second operand to AC
    M[0x002] = 0x3006    # STA 006 / store sum in location 006
    M[0x003] = 0x7001    # HLT / Halt Computer
    M[0x004] = 0x0053    # 0053 / First Operand
    M[0x005] = 0xFFE9    # FFE9 / Second Operand(negative)
    M[0x006] = 0x0000    # 0000 / Store sum here

    # 레지스터 선언
    reg = {
        "PC" : 0x000,   # 12bit / 다음 실행할 명령어 주소
        "AR" : 0x000,   # 12bit / 메모리에 접근할 때 사용할 주소
        "IR" : 0x0000,  # 16bit / 현재 실행중인 명령어
        "DR" : 0x0000,  # 16bit / 메모리에서 읽어온 데이터 저장
        "AC" : 0x0000,  # 16bit / 연산 결과 저장
        "I"  : 0,       # 1bit / Indirect bit        
        "SC" : 0,       # 1bit / sequence counter
        "E"  : 0,       # 1bit / carry 저장용 비트
        "S"  : 1        # 1bit / 컴퓨터 실행/정지 스위치 / 시작 상태이므로 초기값 1
    }
    
    # decode 된 opcode(D0 ~ D7) 저장
    opcode = 0

    # Instruction Cycle
    while(reg["S"] == 1):        
        if(reg["SC"] == 0):
            print(f'------------- Location : {reg["PC"]:03X} -------------\n')
            # T0
            print(f'T{reg["SC"]} : ')
            print("AR <- PC")
            # AR <- PC
            reg["AR"] = reg["PC"]
            print(f'AR = {reg["AR"]:03X}')
            print()
            reg["SC"] = 1

        elif(reg["SC"] == 1):
            # T1
            print(f'T{reg["SC"]} : ')
            print("IR <- M[AR], PC <- PC + 1")
            # IR <- M[AR]
            reg["IR"] = M[reg["AR"]] & 0xFFFF
            # PC <- PC + 1
            reg["PC"] = (reg["PC"] + 1) & 0xFFF
            print(f'IR = {reg["IR"]:04X}, PC = {reg["PC"]:03X}')
            print()
            reg["SC"] = 2
            
        elif(reg["SC"] == 2):
            # T2
            print(f'T{reg["SC"]} : ')
            print("Decode Opcode in IR(12-14)")
            print("AR <- IR(0-11), I <- IR(15)")
            
            # Decode Opcode in IR(12-14)
            opcode = (reg["IR"] >> 12) & 0x7
            
            # AR <- IR(0-11)
            reg["AR"] = (reg["IR"] & 0x0FFF)
            
            # I <- IR(15)
            reg["I"] = (reg["IR"] >> 15) & 0x1
            print(f'D7 = {1 if opcode == 7 else 0}, AR = {reg["AR"]:03X}, I = {reg["I"]}')
            print()
            reg["SC"] = 3
            #reg["S"] = 0
        
        elif(reg["SC"] == 3):
            # T3
            print(f'T{reg["SC"]} : ')
            
            # T3의 세부 동작
            # !D7 and  I T3 : AR <- M[AR]
            # !D7 and !I T3 : no-op
            # D7  and !I T3 : 레지스터 참조 Instruction
            # D7  and  I T3 : I/O Instruction
            
            # !D7 and I T3 : AR <- M[AR]
            # memory reference 방식
            # Indirect(간접) 방식
            # 간접 메모리 참조 명령
            if opcode != 7 and reg["I"] == 1:
                cur_instruction_name = choise_instruction_name(opcode, reg["AR"])
                print(f'instruction : {cur_instruction_name}')
                print("AR <- M[AR]")
                reg["AR"] = M[reg["AR"]] & 0x0FFF
                print(f'AR = {reg["AR"]:03X}')
                print()
                reg["SC"] = 4
            
            # !D7 and !I T3 : no-op(nothing)
            # memory reference 방식
            # Direct(직접) 방식
            # 직접 메모리 참조 명령
            elif opcode != 7 and reg["I"] == 0:
                cur_instruction_name = choise_instruction_name(opcode, reg["AR"])
                print(f'instruction : {cur_instruction_name}')
                print("nothing")
                print()
                reg["SC"] = 4
            
            # D7 and !I T3 : 레지스터 참조 instruction
            # execute register-reference instruction
            elif opcode == 7 and reg["I"] == 0:
                # r = D7 and !I and T3
                # Bi = IR[I]
                # 
                # IR의 0번째 비트가 0이 아닌지 검사
                if reg["IR"] & 0x0001:
                    cur_instruction_name = "HLT"
                # IR의 11번째 비트가 0이 아닌지 검사
                elif reg["IR"] & 0x0800:
                    cur_instruction_name = "CLA"
                else:
                    cur_instruction_name = "register-reference"
                
                print(f'instruction : {cur_instruction_name}')
                
                # rB11 : CLA
                if reg["IR"] & 0x0800:
                    print("rB11: AC <- 0")
                    reg["AC"] = 0
                    print(f'AC = {reg["AC"]:04X}')
                
                # rB0 : HLT
                if reg["IR"] & 0x0001:
                    print("rB0: S <- 0")
                    reg["S"] = 0
                    print(f'S = {reg["S"]}')
                
                # SC <- 0
                print("SC <- 0")
                reg["SC"] = 0
                print(f'SC = {reg["SC"]}')
            
            # D7 and I T3 : I/O Instruction
            # execute input-output instruction
            else:
                print("instruction: input-output")
                print("I/O instruction is not implemented in this simulation")
                print("SC <- 0")
                reg["SC"] = 0
                print(f'SC = {reg["SC"]}')
        
            
        elif reg["SC"] == 4:
            # T4
            # execute memory-reference instruction
            # opcode 0: AND
            # opcode 1: ADD
            # opcode 2: LDA
            # opcode 3: STA
            # opcode 4: BUN
            # opcode 5: BSA
            # opcode 6: ISZ
            print(f'T{reg["SC"]} :')
            
            # AND
            if opcode == 0:
                print("DR <- M[AR]")
                reg["DR"] = M[reg["AR"]]&0xFFFF
                print(f'DR = {reg["DR"]:04X}')
                print()
                reg["SC"] = 5
            # ADD
            elif opcode == 1:
                # 메모리에서 값을 읽어와 Data Register에 저장
                print("DR <- M[AR]")
                reg["DR"] = M[reg["AR"]]&0xFFFF
                print(f'DR = {reg["DR"]:04X}')
                print()
                reg["SC"] = 5
            # LDA
            elif opcode == 2:
                # 메모리에서 값을 읽어와 Data Register에 저장
                print("DR <- M[AR]")
                reg["DR"] = M[reg["AR"]]&0xFFFF
                print(f'DR = {reg["DR"]:04X}')
                print()
                reg["SC"] = 5
            # STA
            elif opcode == 3:
                print("M[AR] <- AC, SC <- 0")
                M[reg["AR"]] = reg["AC"]&0xFFFF
                reg["SC"] = 0
                print(f'M[{reg["AR"]}] = {M[reg["AR"]]:04X}')
                print(f'SC = {reg["SC"]}')
                print()
            # BUN
            elif opcode == 4:   
                print("PC <- AR, SC <- 0")
                reg["PC"] = reg["AR"] & 0xFFF
                reg["SC"] = 0
                print(f'PC = {reg["PC"]:03X}')
                print(f'SC = {reg["SC"]}')
                print()
            # BSA
            elif opcode == 5:
                print("M[AR] <- PC, AR <- AR + 1")
                M[reg["AR"]] = reg["PC"] & 0xFFFF
                reg["AR"] = (reg["AR"] + 1) & 0xFFF
                print(f'M[{(reg["AR"] - 1) & 0xFFF:03X}] = {M[(reg["AR"] - 1) & 0xFFF]:04X}')
                print(f'AR = {reg["AR"]:03X}')
                print()
                reg["SC"] = 5
            # ISZ
            elif opcode == 6:
                print("DR <- M[AR]")
                reg["DR"] = M[reg["AR"]]&0xFFFF
                print(f'DR = {reg["DR"]:04X}')
                print()
                reg["SC"] = 5
                
                
        
        elif reg["SC"] == 5:
            # T5
            print(f'T{reg["SC"]} : ')
            
            # AND
            if opcode == 0:
                print("AC <- AC & DR, SC <- 0")
                reg["AC"] = reg["AC"] & reg["DR"]
                reg["SC"] = 0
                print(f'AC = {reg["AC"]:04X}, SC = {reg["SC"]}')
            # ADD
            elif opcode == 1:
                print("AC <- AC + DR, E <- Cout, SC <- 0")
                tot = reg["AC"] + reg["DR"]
                # AC와 DR의 값에서 캐리가 생길 경우 E 레지스터에 저장
                reg["E"] = 1 if tot > 0xFFFF else 0
                # 캐리 제외 값을 AC 레지스터에 저장
                reg["AC"] = tot & 0xFFFF
                reg["SC"] = 0
                
                print(f'AC = {reg["AC"]:04X}, E = {reg["E"]}')
                print(f'SC = {reg["SC"]}')
            # LDA
            elif opcode == 2:
                print("AC <- DR, SC <- 0")
                reg["AC"] = reg["DR"] & 0xFFFF
                reg["SC"] = 0
                
                print(f'AC = {reg["AC"]:04X}, SC = {reg["SC"]}')
            # BSA
            elif opcode == 5:
                print("PC <- AR, SC <- 0")
                reg["PC"] = reg["AR"]
                reg["SC"] = 0
                print(f'PC = {reg["PC"]:03X}, SC = {reg["SC"]}')
            # ISZ
            elif opcode == 6:
                print("DR <- DR + 1")
                reg["DR"] = (reg["DR"] + 1) & 0xFFFF
                print(f'DR = {reg["DR"]:04X}')
                print()
                reg["SC"] = 6
        
        elif reg["SC"] == 6:
            # T6
            print(f'T{reg["SC"]} : ')
            
            # ISZ
            print("M[AR] <- DR, if (DR == 0) then PC <- PC + 1, SC <- 0")
            M[reg["AR"]] = reg["DR"] & 0xFFFF

            if reg["DR"] == 0:
                reg["PC"] = (reg["PC"] + 1) & 0xFFF
            reg["SC"] = 0

            print(f'M[{reg["AR"]:03X}] = {M[reg["AR"]]:04X}')
            print(f'PC = {reg["PC"]:03X}')
            print(f'SC = {reg["SC"]}')
            print()
                

    final_register(reg)
    final_memory(M)

                
                
if __name__ == "__main__":
    simulate_cycle()



        