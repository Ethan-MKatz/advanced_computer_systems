	.file	"benchmark_day3_alignment.cpp"
	.intel_syntax noprefix
	.text
#APP
	.globl _ZSt21ios_base_library_initv
#NO_APP
	.p2align 4
	.type	_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEEldNS0_5__ops15_Iter_less_iterEEvT_T0_SA_T1_T2_.isra.0, @function
_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEEldNS0_5__ops15_Iter_less_iterEEvT_T0_SA_T1_T2_.isra.0:
.LFB4415:
	.cfi_startproc
	lea	rax, -1[rdx]
	push	rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	mov	rbx, rdx
	mov	rcx, rdi
	mov	r10, rax
	mov	rdi, rsi
	mov	r11, rdx
	and	ebx, 1
	shr	r10, 63
	add	r10, rax
	sar	r10
	cmp	rsi, r10
	jl	.L5
	jmp	.L2
	.p2align 4,,10
	.p2align 3
.L11:
	mov	rsi, rdx
.L5:
	lea	rax, 1[rsi]
	lea	rdx, [rax+rax]
	sal	rax, 4
	lea	r8, -1[rdx]
	add	rax, rcx
	lea	r9, [rcx+r8*8]
	vmovsd	xmm1, QWORD PTR [rax]
	vmovsd	xmm2, QWORD PTR [r9]
	vcomisd	xmm2, xmm1
	jbe	.L3
	vmovsd	xmm1, xmm2, xmm2
	mov	rax, r9
	mov	rdx, r8
.L3:
	vmovsd	QWORD PTR [rcx+rsi*8], xmm1
	cmp	r10, rdx
	jg	.L11
	test	rbx, rbx
	je	.L10
.L6:
	lea	r8, -1[rdx]
	mov	rsi, r8
	shr	rsi, 63
	add	rsi, r8
	sar	rsi
	cmp	rdx, rdi
	jg	.L9
	jmp	.L7
	.p2align 4,,10
	.p2align 3
.L21:
	lea	rdx, -1[rsi]
	vmovsd	QWORD PTR [rax], xmm1
	mov	rax, rdx
	shr	rax, 63
	add	rax, rdx
	mov	rdx, rsi
	sar	rax
	cmp	rdi, rsi
	jge	.L20
	mov	rsi, rax
.L9:
	lea	r8, [rcx+rsi*8]
	lea	rax, [rcx+rdx*8]
	vmovsd	xmm1, QWORD PTR [r8]
	vcomisd	xmm0, xmm1
	ja	.L21
.L7:
	vmovsd	QWORD PTR [rax], xmm0
	pop	rbx
	.cfi_remember_state
	.cfi_def_cfa_offset 8
	ret
	.p2align 4,,10
	.p2align 3
.L2:
	.cfi_restore_state
	lea	rax, [rcx+rsi*8]
	test	rbx, rbx
	jne	.L7
	mov	rdx, rdi
	.p2align 4,,10
	.p2align 3
.L10:
	sub	r11, 2
	mov	rsi, r11
	shr	rsi, 63
	add	rsi, r11
	sar	rsi
	cmp	rdx, rsi
	jne	.L6
	lea	rdx, 1[rdx+rdx]
	lea	rsi, [rcx+rdx*8]
	vmovsd	xmm1, QWORD PTR [rsi]
	vmovsd	QWORD PTR [rax], xmm1
	mov	rax, rsi
	jmp	.L6
	.p2align 4,,10
	.p2align 3
.L20:
	mov	rax, r8
	vmovsd	QWORD PTR [rax], xmm0
	pop	rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE4415:
	.size	_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEEldNS0_5__ops15_Iter_less_iterEEvT_T0_SA_T1_T2_.isra.0, .-_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEEldNS0_5__ops15_Iter_less_iterEEvT_T0_SA_T1_T2_.isra.0
	.p2align 4
	.type	_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEElNS0_5__ops15_Iter_less_iterEEvT_S9_T0_T1_.isra.0, @function
_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEElNS0_5__ops15_Iter_less_iterEEvT_S9_T0_T1_.isra.0:
.LFB4416:
	.cfi_startproc
	mov	rax, rsi
	mov	rcx, rsi
	sub	rax, rdi
	cmp	rax, 128
	jle	.L79
	push	r13
	.cfi_def_cfa_offset 16
	.cfi_offset 13, -16
	mov	r13, rdx
	push	r12
	.cfi_def_cfa_offset 24
	.cfi_offset 12, -24
	mov	r12, rdi
	push	rbp
	.cfi_def_cfa_offset 32
	.cfi_offset 6, -32
	lea	rbp, 8[rdi]
	push	rbx
	.cfi_def_cfa_offset 40
	.cfi_offset 3, -40
	sub	rsp, 8
	.cfi_def_cfa_offset 48
	test	rdx, rdx
	je	.L80
.L25:
	sar	rax, 4
	sub	r13, 1
	vmovsd	xmm1, QWORD PTR 8[r12]
	vpermilpd	xmm4, XMMWORD PTR [r12], 1
	lea	rax, [r12+rax*8]
	vmovsd	xmm0, QWORD PTR [r12]
	vmovsd	xmm3, QWORD PTR -8[rsi]
	vmovsd	xmm2, QWORD PTR [rax]
	vcomisd	xmm2, xmm1
	jbe	.L67
	vcomisd	xmm3, xmm2
	ja	.L71
	vcomisd	xmm3, xmm1
	ja	.L78
.L69:
	vmovupd	XMMWORD PTR [r12], xmm4
	vmovsd	xmm2, QWORD PTR -8[rsi]
.L35:
	mov	rdx, rsi
	mov	rcx, rbp
	.p2align 4,,10
	.p2align 3
.L38:
	vcomisd	xmm1, xmm0
	lea	rax, 8[rcx]
	jbe	.L72
	.p2align 4,,10
	.p2align 3
.L45:
	mov	rcx, rax
	vmovsd	xmm0, QWORD PTR [rax]
	add	rax, 8
	vcomisd	xmm1, xmm0
	ja	.L45
.L72:
	sub	rdx, 8
	vcomisd	xmm2, xmm1
	mov	rbx, rcx
	jbe	.L46
	.p2align 4,,10
	.p2align 3
.L48:
	vmovsd	xmm2, QWORD PTR -8[rdx]
	sub	rdx, 8
	vcomisd	xmm2, xmm1
	ja	.L48
.L46:
	cmp	rbx, rdx
	jnb	.L81
	vmovsd	QWORD PTR [rbx], xmm2
	lea	rcx, 8[rbx]
	vmovsd	xmm2, QWORD PTR -8[rdx]
	vmovsd	QWORD PTR [rdx], xmm0
	vmovsd	xmm1, QWORD PTR [r12]
	vmovsd	xmm0, QWORD PTR 8[rbx]
	jmp	.L38
.L67:
	vcomisd	xmm3, xmm1
	ja	.L69
	vcomisd	xmm3, xmm2
	jbe	.L71
.L78:
	vmovsd	QWORD PTR [r12], xmm3
	vmovsd	xmm2, xmm0, xmm0
	vmovsd	QWORD PTR -8[rsi], xmm0
	vmovsd	xmm1, QWORD PTR [r12]
	vmovsd	xmm0, QWORD PTR 8[r12]
	jmp	.L35
	.p2align 4,,10
	.p2align 3
.L81:
	mov	rdx, r13
	mov	rdi, rbx
	call	_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEElNS0_5__ops15_Iter_less_iterEEvT_S9_T0_T1_.isra.0
	mov	rax, rbx
	sub	rax, r12
	cmp	rax, 128
	jle	.L74
	test	r13, r13
	je	.L51
	mov	rsi, rbx
	jmp	.L25
.L71:
	vmovsd	QWORD PTR [r12], xmm2
	vmovsd	QWORD PTR [rax], xmm0
	vmovsd	xmm0, QWORD PTR 8[r12]
	vmovsd	xmm1, QWORD PTR [r12]
	vmovsd	xmm2, QWORD PTR -8[rsi]
	jmp	.L35
.L80:
	mov	rbx, rcx
.L51:
	sar	rax, 3
	lea	r13, -2[rax]
	mov	rbp, rax
	sar	r13
	jmp	.L27
.L82:
	sub	r13, 1
.L27:
	vmovsd	xmm0, QWORD PTR [r12+r13*8]
	mov	rdx, rbp
	mov	rsi, r13
	mov	rdi, r12
	call	_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEEldNS0_5__ops15_Iter_less_iterEEvT_T0_SA_T1_T2_.isra.0
	test	r13, r13
	jne	.L82
	sub	rbx, 8
	.p2align 4,,10
	.p2align 3
.L28:
	mov	rbp, rbx
	vmovsd	xmm1, QWORD PTR [r12]
	vmovsd	xmm0, QWORD PTR [rbx]
	xor	esi, esi
	sub	rbp, r12
	mov	rdi, r12
	sub	rbx, 8
	mov	rdx, rbp
	vmovsd	QWORD PTR 8[rbx], xmm1
	sar	rdx, 3
	call	_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEEldNS0_5__ops15_Iter_less_iterEEvT_T0_SA_T1_T2_.isra.0
	cmp	rbp, 8
	jg	.L28
.L74:
	add	rsp, 8
	.cfi_def_cfa_offset 40
	pop	rbx
	.cfi_def_cfa_offset 32
	pop	rbp
	.cfi_def_cfa_offset 24
	pop	r12
	.cfi_def_cfa_offset 16
	pop	r13
	.cfi_def_cfa_offset 8
	ret
.L79:
	.cfi_restore 3
	.cfi_restore 6
	.cfi_restore 12
	.cfi_restore 13
	ret
	.cfi_endproc
.LFE4416:
	.size	_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEElNS0_5__ops15_Iter_less_iterEEvT_S9_T0_T1_.isra.0, .-_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEElNS0_5__ops15_Iter_less_iterEEvT_S9_T0_T1_.isra.0
	.section	.rodata.str1.1,"aMS",@progbits,1
.LC0:
	.string	"Memory allocation failed\n"
	.text
	.p2align 4
	.globl	_Z16allocate_alignedm
	.type	_Z16allocate_alignedm, @function
_Z16allocate_alignedm:
.LFB3509:
	.cfi_startproc
	endbr64
	sub	rsp, 24
	.cfi_def_cfa_offset 32
	lea	rdx, 0[0+rdi*4]
	mov	esi, 64
	mov	rax, QWORD PTR fs:40
	mov	QWORD PTR 8[rsp], rax
	xor	eax, eax
	mov	rdi, rsp
	mov	QWORD PTR [rsp], 0
	call	posix_memalign@PLT
	test	eax, eax
	jne	.L87
	mov	rax, QWORD PTR [rsp]
	mov	rdx, QWORD PTR 8[rsp]
	sub	rdx, QWORD PTR fs:40
	jne	.L88
	add	rsp, 24
	.cfi_remember_state
	.cfi_def_cfa_offset 8
	ret
.L87:
	.cfi_restore_state
	lea	rdi, _ZSt4cerr[rip]
	mov	edx, 25
	lea	rsi, .LC0[rip]
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	edi, 1
	call	exit@PLT
.L88:
	call	__stack_chk_fail@PLT
	.cfi_endproc
.LFE3509:
	.size	_Z16allocate_alignedm, .-_Z16allocate_alignedm
	.p2align 4
	.globl	_Z8multiplyPKfS0_Pfm
	.type	_Z8multiplyPKfS0_Pfm, @function
_Z8multiplyPKfS0_Pfm:
.LFB3510:
	.cfi_startproc
	endbr64
	test	rcx, rcx
	je	.L121
	lea	rax, -1[rcx]
	cmp	rax, 2
	jbe	.L100
	lea	r9, 4[rdi]
	mov	r8, rdx
	sub	r8, r9
	cmp	r8, 24
	jbe	.L100
	lea	r9, 4[rsi]
	mov	r8, rdx
	sub	r8, r9
	cmp	r8, 24
	jbe	.L100
	mov	r8, rcx
	cmp	rax, 6
	jbe	.L101
	shr	r8, 3
	xor	eax, eax
	sal	r8, 5
	.p2align 4,,10
	.p2align 3
.L93:
	vmovups	ymm1, YMMWORD PTR [rdi+rax]
	vmulps	ymm0, ymm1, YMMWORD PTR [rsi+rax]
	vmovups	YMMWORD PTR [rdx+rax], ymm0
	add	rax, 32
	cmp	rax, r8
	jne	.L93
	mov	rax, rcx
	and	rax, -8
	test	cl, 7
	je	.L119
	mov	r8, rcx
	sub	r8, rax
	lea	r9, -1[r8]
	cmp	r9, 2
	jbe	.L122
	vzeroupper
.L92:
	vmovups	xmm2, XMMWORD PTR [rdi+rax*4]
	vmulps	xmm0, xmm2, XMMWORD PTR [rsi+rax*4]
	mov	r9, r8
	and	r9, -4
	vmovups	XMMWORD PTR [rdx+rax*4], xmm0
	add	rax, r9
	and	r8d, 3
	je	.L121
.L95:
	vmovss	xmm0, DWORD PTR [rdi+rax*4]
	vmulss	xmm0, xmm0, DWORD PTR [rsi+rax*4]
	lea	r9, 1[rax]
	lea	r8, 0[0+rax*4]
	vmovss	DWORD PTR [rdx+rax*4], xmm0
	cmp	r9, rcx
	jnb	.L121
	vmovss	xmm0, DWORD PTR 4[rdi+r8]
	vmulss	xmm0, xmm0, DWORD PTR 4[rsi+r8]
	add	rax, 2
	vmovss	DWORD PTR 4[rdx+r8], xmm0
	cmp	rax, rcx
	jnb	.L121
	vmovss	xmm0, DWORD PTR 8[rdi+r8]
	vmulss	xmm0, xmm0, DWORD PTR 8[rsi+r8]
	vmovss	DWORD PTR 8[rdx+r8], xmm0
	ret
	.p2align 4,,10
	.p2align 3
.L100:
	xor	eax, eax
	.p2align 4,,10
	.p2align 3
.L97:
	vmovss	xmm0, DWORD PTR [rdi+rax*4]
	vmulss	xmm0, xmm0, DWORD PTR [rsi+rax*4]
	vmovss	DWORD PTR [rdx+rax*4], xmm0
	add	rax, 1
	cmp	rcx, rax
	jne	.L97
	ret
.L119:
	vzeroupper
.L121:
	ret
.L101:
	xor	eax, eax
	jmp	.L92
.L122:
	vzeroupper
	jmp	.L95
	.cfi_endproc
.LFE3510:
	.size	_Z8multiplyPKfS0_Pfm, .-_Z8multiplyPKfS0_Pfm
	.p2align 4
	.globl	_Z6medianSt6vectorIdSaIdEE
	.type	_Z6medianSt6vectorIdSaIdEE, @function
_Z6medianSt6vectorIdSaIdEE:
.LFB3511:
	.cfi_startproc
	endbr64
	push	r15
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
	push	r14
	.cfi_def_cfa_offset 24
	.cfi_offset 14, -24
	push	r13
	.cfi_def_cfa_offset 32
	.cfi_offset 13, -32
	push	r12
	.cfi_def_cfa_offset 40
	.cfi_offset 12, -40
	push	rbp
	.cfi_def_cfa_offset 48
	.cfi_offset 6, -48
	push	rbx
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	sub	rsp, 24
	.cfi_def_cfa_offset 80
	mov	r13, QWORD PTR 8[rdi]
	mov	rbp, QWORD PTR [rdi]
	mov	r15, r13
	sub	r15, rbp
	mov	rax, r15
	sar	rax, 3
	mov	r14, rax
	cmp	rbp, r13
	je	.L125
	mov	edx, 63
	lzcnt	rax, rax
	mov	r12, rdi
	mov	rsi, r13
	sub	edx, eax
	mov	rdi, rbp
	lea	rbx, 8[rbp]
	movsx	rdx, edx
	add	rdx, rdx
	call	_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPdSt6vectorIdSaIdEEEElNS0_5__ops15_Iter_less_iterEEvT_S9_T0_T1_.isra.0
	cmp	r15, 128
	jg	.L167
	cmp	r13, rbx
	je	.L125
	mov	r14d, 8
	jmp	.L150
	.p2align 4,,10
	.p2align 3
.L169:
	sub	rdx, rbp
	cmp	rdx, 8
	jle	.L144
	mov	rdi, r14
	mov	rsi, rbp
	vmovsd	QWORD PTR 8[rsp], xmm1
	sub	rdi, rdx
	add	rdi, rbx
	call	memmove@PLT
	vmovsd	xmm1, QWORD PTR 8[rsp]
.L145:
	add	rbx, 8
	vmovsd	QWORD PTR 0[rbp], xmm1
	cmp	r13, rbx
	je	.L168
.L150:
	vmovsd	xmm1, QWORD PTR [rbx]
	vmovsd	xmm0, QWORD PTR 0[rbp]
	mov	rdx, rbx
	vcomisd	xmm0, xmm1
	ja	.L169
	vmovsd	xmm0, QWORD PTR -8[rbx]
	lea	rax, -8[rbx]
	vcomisd	xmm0, xmm1
	jbe	.L147
	.p2align 4,,10
	.p2align 3
.L149:
	vmovsd	QWORD PTR 8[rax], xmm0
	mov	rdx, rax
	vmovsd	xmm0, QWORD PTR -8[rax]
	sub	rax, 8
	vcomisd	xmm0, xmm1
	ja	.L149
.L147:
	add	rbx, 8
	vmovsd	QWORD PTR [rdx], xmm1
	cmp	r13, rbx
	jne	.L150
.L168:
	mov	rbp, QWORD PTR [r12]
	mov	r14, QWORD PTR 8[r12]
	sub	r14, rbp
	sar	r14, 3
.L125:
	shr	r14
	vmovsd	xmm0, QWORD PTR 0[rbp+r14*8]
	add	rsp, 24
	.cfi_remember_state
	.cfi_def_cfa_offset 56
	pop	rbx
	.cfi_def_cfa_offset 48
	pop	rbp
	.cfi_def_cfa_offset 40
	pop	r12
	.cfi_def_cfa_offset 32
	pop	r13
	.cfi_def_cfa_offset 24
	pop	r14
	.cfi_def_cfa_offset 16
	pop	r15
	.cfi_def_cfa_offset 8
	ret
	.p2align 4,,10
	.p2align 3
.L167:
	.cfi_restore_state
	lea	r15, 128[rbp]
	mov	r14d, 8
	jmp	.L135
	.p2align 4,,10
	.p2align 3
.L171:
	sub	rdx, rbp
	cmp	rdx, 8
	jle	.L129
	mov	rdi, r14
	mov	rsi, rbp
	vmovsd	QWORD PTR 8[rsp], xmm1
	sub	rdi, rdx
	add	rdi, rbx
	call	memmove@PLT
	vmovsd	xmm1, QWORD PTR 8[rsp]
.L130:
	add	rbx, 8
	vmovsd	QWORD PTR 0[rbp], xmm1
	cmp	r15, rbx
	je	.L170
.L135:
	vmovsd	xmm1, QWORD PTR [rbx]
	vmovsd	xmm0, QWORD PTR 0[rbp]
	mov	rdx, rbx
	vcomisd	xmm0, xmm1
	ja	.L171
	vmovsd	xmm0, QWORD PTR -8[rbx]
	lea	rax, -8[rbx]
	vcomisd	xmm0, xmm1
	jbe	.L132
	.p2align 4,,10
	.p2align 3
.L134:
	vmovsd	QWORD PTR 8[rax], xmm0
	mov	rdx, rax
	vmovsd	xmm0, QWORD PTR -8[rax]
	sub	rax, 8
	vcomisd	xmm0, xmm1
	ja	.L134
.L132:
	add	rbx, 8
	vmovsd	QWORD PTR [rdx], xmm1
	cmp	r15, rbx
	jne	.L135
.L170:
	mov	rbp, QWORD PTR [r12]
	mov	r14, QWORD PTR 8[r12]
	sub	r14, rbp
	sar	r14, 3
	cmp	r13, r15
	je	.L125
	.p2align 4,,10
	.p2align 3
.L140:
	vmovsd	xmm1, QWORD PTR [r15]
	vmovsd	xmm0, QWORD PTR -8[r15]
	lea	rax, -8[r15]
	vcomisd	xmm0, xmm1
	jbe	.L164
	.p2align 4,,10
	.p2align 3
.L139:
	vmovsd	QWORD PTR 8[rax], xmm0
	mov	rdx, rax
	vmovsd	xmm0, QWORD PTR -8[rax]
	sub	rax, 8
	vcomisd	xmm0, xmm1
	ja	.L139
	add	r15, 8
	vmovsd	QWORD PTR [rdx], xmm1
	cmp	r13, r15
	jne	.L140
	jmp	.L125
	.p2align 4,,10
	.p2align 3
.L164:
	mov	rdx, r15
	add	r15, 8
	vmovsd	QWORD PTR [rdx], xmm1
	cmp	r13, r15
	jne	.L140
	jmp	.L125
.L144:
	jne	.L145
	vmovsd	QWORD PTR [rbx], xmm0
	jmp	.L145
.L129:
	jne	.L130
	vmovsd	QWORD PTR [rbx], xmm0
	jmp	.L130
	.cfi_endproc
.LFE3511:
	.size	_Z6medianSt6vectorIdSaIdEE, .-_Z6medianSt6vectorIdSaIdEE
	.section	.text._ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_,"axG",@progbits,_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_,comdat
	.p2align 4
	.weak	_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_
	.type	_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_, @function
_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_:
.LFB3663:
	.cfi_startproc
	.cfi_personality 0x9b,DW.ref.__gxx_personality_v0
	.cfi_lsda 0x1b,.LLSDA3663
	endbr64
	push	r15
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
	mov	r15, rdi
	push	r14
	.cfi_def_cfa_offset 24
	.cfi_offset 14, -24
	mov	r14d, r8d
	push	r13
	.cfi_def_cfa_offset 32
	.cfi_offset 13, -32
	push	r12
	.cfi_def_cfa_offset 40
	.cfi_offset 12, -40
	mov	r12, rcx
	push	rbp
	.cfi_def_cfa_offset 48
	.cfi_offset 6, -48
	mov	rbp, rdx
	push	rbx
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	sub	rsp, 40
	.cfi_def_cfa_offset 96
	mov	QWORD PTR 8[rsp], rsi
	mov	rax, QWORD PTR fs:40
	mov	QWORD PTR 24[rsp], rax
	xor	eax, eax
	call	__errno_location@PLT
	lea	rsi, 16[rsp]
	mov	edx, r14d
	mov	rdi, rbp
	mov	r13d, DWORD PTR [rax]
	mov	rbx, rax
	mov	DWORD PTR [rax], 0
.LEHB0:
	call	r15
	mov	rdx, QWORD PTR 16[rsp]
	cmp	rdx, rbp
	je	.L190
	mov	ecx, DWORD PTR [rbx]
	cmp	ecx, 34
	je	.L191
	test	r12, r12
	je	.L177
	sub	rdx, rbp
	mov	QWORD PTR [r12], rdx
.L177:
	test	ecx, ecx
	je	.L192
.L172:
	mov	rdx, QWORD PTR 24[rsp]
	sub	rdx, QWORD PTR fs:40
	jne	.L189
	add	rsp, 40
	.cfi_remember_state
	.cfi_def_cfa_offset 56
	pop	rbx
	.cfi_def_cfa_offset 48
	pop	rbp
	.cfi_def_cfa_offset 40
	pop	r12
	.cfi_def_cfa_offset 32
	pop	r13
	.cfi_def_cfa_offset 24
	pop	r14
	.cfi_def_cfa_offset 16
	pop	r15
	.cfi_def_cfa_offset 8
	ret
	.p2align 4,,10
	.p2align 3
.L192:
	.cfi_restore_state
	mov	DWORD PTR [rbx], r13d
	jmp	.L172
.L191:
	mov	rax, QWORD PTR 24[rsp]
	sub	rax, QWORD PTR fs:40
	jne	.L189
	mov	rdi, QWORD PTR 8[rsp]
	call	_ZSt20__throw_out_of_rangePKc@PLT
.L190:
	mov	rax, QWORD PTR 24[rsp]
	sub	rax, QWORD PTR fs:40
	jne	.L189
	mov	rdi, QWORD PTR 8[rsp]
	call	_ZSt24__throw_invalid_argumentPKc@PLT
.LEHE0:
.L189:
	call	__stack_chk_fail@PLT
.L183:
	endbr64
	mov	rdi, rax
.L179:
	cmp	DWORD PTR [rbx], 0
	jne	.L180
	mov	DWORD PTR [rbx], r13d
.L180:
	mov	rax, QWORD PTR 24[rsp]
	sub	rax, QWORD PTR fs:40
	jne	.L193
	vzeroupper
.LEHB1:
	call	_Unwind_Resume@PLT
.LEHE1:
.L193:
	vzeroupper
	call	__stack_chk_fail@PLT
	.cfi_endproc
.LFE3663:
	.globl	__gxx_personality_v0
	.section	.gcc_except_table._ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_,"aG",@progbits,_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_,comdat
.LLSDA3663:
	.byte	0xff
	.byte	0xff
	.byte	0x1
	.uleb128 .LLSDACSE3663-.LLSDACSB3663
.LLSDACSB3663:
	.uleb128 .LEHB0-.LFB3663
	.uleb128 .LEHE0-.LEHB0
	.uleb128 .L183-.LFB3663
	.uleb128 0
	.uleb128 .LEHB1-.LFB3663
	.uleb128 .LEHE1-.LEHB1
	.uleb128 0
	.uleb128 0
.LLSDACSE3663:
	.section	.text._ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_,"axG",@progbits,_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_,comdat
	.size	_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_, .-_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_
	.section	.rodata._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.str1.8,"aMS",@progbits,1
	.align 8
.LC1:
	.string	"basic_string: construction from null is not valid"
	.section	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_,"axG",@progbits,_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC5IS3_EEPKcRKS3_,comdat
	.align 2
	.p2align 4
	.weak	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_
	.type	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_, @function
_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_:
.LFB3876:
	.cfi_startproc
	endbr64
	push	r13
	.cfi_def_cfa_offset 16
	.cfi_offset 13, -16
	lea	r13, 16[rdi]
	push	r12
	.cfi_def_cfa_offset 24
	.cfi_offset 12, -24
	push	rbp
	.cfi_def_cfa_offset 32
	.cfi_offset 6, -32
	push	rbx
	.cfi_def_cfa_offset 40
	.cfi_offset 3, -40
	sub	rsp, 24
	.cfi_def_cfa_offset 64
	mov	rax, QWORD PTR fs:40
	mov	QWORD PTR 8[rsp], rax
	xor	eax, eax
	mov	QWORD PTR [rdi], r13
	test	rsi, rsi
	je	.L208
	mov	rbx, rdi
	mov	rdi, rsi
	mov	r12, rsi
	call	strlen@PLT
	mov	QWORD PTR [rsp], rax
	mov	rbp, rax
	cmp	rax, 15
	ja	.L209
	cmp	rax, 1
	jne	.L199
	movzx	edx, BYTE PTR [r12]
	mov	BYTE PTR 16[rbx], dl
.L200:
	mov	QWORD PTR 8[rbx], rax
	mov	BYTE PTR 0[r13+rax], 0
	mov	rax, QWORD PTR 8[rsp]
	sub	rax, QWORD PTR fs:40
	jne	.L207
	add	rsp, 24
	.cfi_remember_state
	.cfi_def_cfa_offset 40
	pop	rbx
	.cfi_def_cfa_offset 32
	pop	rbp
	.cfi_def_cfa_offset 24
	pop	r12
	.cfi_def_cfa_offset 16
	pop	r13
	.cfi_def_cfa_offset 8
	ret
	.p2align 4,,10
	.p2align 3
.L199:
	.cfi_restore_state
	test	rax, rax
	je	.L200
	jmp	.L198
	.p2align 4,,10
	.p2align 3
.L209:
	mov	rsi, rsp
	xor	edx, edx
	mov	rdi, rbx
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@PLT
	mov	QWORD PTR [rbx], rax
	mov	r13, rax
	mov	rax, QWORD PTR [rsp]
	mov	QWORD PTR 16[rbx], rax
.L198:
	mov	rdi, r13
	mov	rdx, rbp
	mov	rsi, r12
	call	memcpy@PLT
	mov	rax, QWORD PTR [rsp]
	mov	r13, QWORD PTR [rbx]
	jmp	.L200
.L207:
	call	__stack_chk_fail@PLT
.L208:
	mov	rax, QWORD PTR 8[rsp]
	sub	rax, QWORD PTR fs:40
	jne	.L207
	lea	rdi, .LC1[rip]
	call	_ZSt19__throw_logic_errorPKc@PLT
	.cfi_endproc
.LFE3876:
	.size	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_, .-_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_
	.weak	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3_
	.set	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3_,_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_
	.section	.text._ZNSt6vectorIdSaIdEED2Ev,"axG",@progbits,_ZNSt6vectorIdSaIdEED5Ev,comdat
	.align 2
	.p2align 4
	.weak	_ZNSt6vectorIdSaIdEED2Ev
	.type	_ZNSt6vectorIdSaIdEED2Ev, @function
_ZNSt6vectorIdSaIdEED2Ev:
.LFB3889:
	.cfi_startproc
	endbr64
	mov	rax, QWORD PTR [rdi]
	test	rax, rax
	je	.L212
	mov	rsi, QWORD PTR 16[rdi]
	mov	rdi, rax
	sub	rsi, rax
	jmp	_ZdlPvm@PLT
	.p2align 4,,10
	.p2align 3
.L212:
	ret
	.cfi_endproc
.LFE3889:
	.size	_ZNSt6vectorIdSaIdEED2Ev, .-_ZNSt6vectorIdSaIdEED2Ev
	.weak	_ZNSt6vectorIdSaIdEED1Ev
	.set	_ZNSt6vectorIdSaIdEED1Ev,_ZNSt6vectorIdSaIdEED2Ev
	.section	.text._ZNSt6vectorIdSaIdEEC2ERKS1_,"axG",@progbits,_ZNSt6vectorIdSaIdEEC5ERKS1_,comdat
	.align 2
	.p2align 4
	.weak	_ZNSt6vectorIdSaIdEEC2ERKS1_
	.type	_ZNSt6vectorIdSaIdEEC2ERKS1_, @function
_ZNSt6vectorIdSaIdEEC2ERKS1_:
.LFB3909:
	.cfi_startproc
	endbr64
	push	r12
	.cfi_def_cfa_offset 16
	.cfi_offset 12, -16
	vpxor	xmm0, xmm0, xmm0
	mov	r12, rsi
	push	rbp
	.cfi_def_cfa_offset 24
	.cfi_offset 6, -24
	mov	rbp, rdi
	push	rbx
	.cfi_def_cfa_offset 32
	.cfi_offset 3, -32
	mov	rbx, QWORD PTR 8[rsi]
	sub	rbx, QWORD PTR [rsi]
	mov	QWORD PTR 16[rdi], 0
	vmovdqu	XMMWORD PTR [rdi], xmm0
	je	.L219
	movabs	rax, 9223372036854775800
	cmp	rax, rbx
	jb	.L221
	mov	rdi, rbx
	call	_Znwm@PLT
	mov	rcx, rax
.L214:
	vmovq	xmm1, rcx
	add	rbx, rcx
	vpunpcklqdq	xmm0, xmm1, xmm1
	mov	QWORD PTR 16[rbp], rbx
	vmovdqu	XMMWORD PTR 0[rbp], xmm0
	mov	rsi, QWORD PTR [r12]
	mov	rax, QWORD PTR 8[r12]
	sub	rax, rsi
	cmp	rax, 8
	jle	.L216
	mov	rdi, rcx
	mov	rdx, rax
	mov	rbx, rax
	call	memmove@PLT
	mov	rcx, rax
.L217:
	add	rcx, rbx
	mov	QWORD PTR 8[rbp], rcx
	pop	rbx
	.cfi_remember_state
	.cfi_def_cfa_offset 24
	pop	rbp
	.cfi_def_cfa_offset 16
	pop	r12
	.cfi_def_cfa_offset 8
	ret
	.p2align 4,,10
	.p2align 3
.L219:
	.cfi_restore_state
	xor	ecx, ecx
	jmp	.L214
	.p2align 4,,10
	.p2align 3
.L216:
	mov	rbx, rax
	jne	.L217
	vmovsd	xmm0, QWORD PTR [rsi]
	mov	ebx, 8
	vmovsd	QWORD PTR [rcx], xmm0
	jmp	.L217
	.p2align 4,,10
	.p2align 3
.L221:
	call	_ZSt28__throw_bad_array_new_lengthv@PLT
	.cfi_endproc
.LFE3909:
	.size	_ZNSt6vectorIdSaIdEEC2ERKS1_, .-_ZNSt6vectorIdSaIdEEC2ERKS1_
	.weak	_ZNSt6vectorIdSaIdEEC1ERKS1_
	.set	_ZNSt6vectorIdSaIdEEC1ERKS1_,_ZNSt6vectorIdSaIdEEC2ERKS1_
	.section	.rodata._ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_.str1.1,"aMS",@progbits,1
.LC2:
	.string	"vector::_M_realloc_insert"
	.section	.text._ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_,"axG",@progbits,_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_,comdat
	.align 2
	.p2align 4
	.weak	_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_
	.type	_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_, @function
_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_:
.LFB4084:
	.cfi_startproc
	endbr64
	push	r15
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
	mov	r15, rdx
	movabs	rdx, 1152921504606846975
	push	r14
	.cfi_def_cfa_offset 24
	.cfi_offset 14, -24
	push	r13
	.cfi_def_cfa_offset 32
	.cfi_offset 13, -32
	push	r12
	.cfi_def_cfa_offset 40
	.cfi_offset 12, -40
	push	rbp
	.cfi_def_cfa_offset 48
	.cfi_offset 6, -48
	push	rbx
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	sub	rsp, 24
	.cfi_def_cfa_offset 80
	mov	r12, QWORD PTR 8[rdi]
	mov	r13, QWORD PTR [rdi]
	mov	rax, r12
	sub	rax, r13
	sar	rax, 3
	cmp	rax, rdx
	je	.L245
	mov	rdx, rsi
	mov	rbp, rdi
	mov	r14, rsi
	sub	rdx, r13
	cmp	r13, r12
	je	.L246
	lea	rcx, [rax+rax]
	cmp	rcx, rax
	jb	.L237
	test	rcx, rcx
	jne	.L247
	xor	ebx, ebx
	xor	ecx, ecx
.L228:
	vmovsd	xmm0, QWORD PTR [r15]
	lea	r8, 8[rcx+rdx]
	sub	r12, r14
	lea	r15, [r8+r12]
	vmovsd	QWORD PTR [rcx+rdx], xmm0
	test	rdx, rdx
	jg	.L248
	test	r12, r12
	jle	.L232
	mov	rdx, r12
	mov	rsi, r14
	mov	rdi, r8
	mov	QWORD PTR [rsp], rcx
	call	memcpy@PLT
	mov	rcx, QWORD PTR [rsp]
.L232:
	test	r13, r13
	jne	.L231
.L234:
	mov	QWORD PTR 0[rbp], rcx
	mov	QWORD PTR 8[rbp], r15
	mov	QWORD PTR 16[rbp], rbx
	add	rsp, 24
	.cfi_remember_state
	.cfi_def_cfa_offset 56
	pop	rbx
	.cfi_def_cfa_offset 48
	pop	rbp
	.cfi_def_cfa_offset 40
	pop	r12
	.cfi_def_cfa_offset 32
	pop	r13
	.cfi_def_cfa_offset 24
	pop	r14
	.cfi_def_cfa_offset 16
	pop	r15
	.cfi_def_cfa_offset 8
	ret
	.p2align 4,,10
	.p2align 3
.L237:
	.cfi_restore_state
	movabs	rbx, 9223372036854775800
.L227:
	mov	rdi, rbx
	mov	QWORD PTR [rsp], rdx
	call	_Znwm@PLT
	mov	rdx, QWORD PTR [rsp]
	mov	rcx, rax
	add	rbx, rax
	jmp	.L228
	.p2align 4,,10
	.p2align 3
.L248:
	mov	rdi, rcx
	mov	rsi, r13
	mov	QWORD PTR [rsp], r8
	call	memmove@PLT
	mov	rcx, rax
	test	r12, r12
	jg	.L249
.L231:
	mov	rsi, QWORD PTR 16[rbp]
	mov	rdi, r13
	mov	QWORD PTR [rsp], rcx
	sub	rsi, r13
	call	_ZdlPvm@PLT
	mov	rcx, QWORD PTR [rsp]
	jmp	.L234
	.p2align 4,,10
	.p2align 3
.L246:
	add	rax, 1
	jc	.L237
	movabs	rcx, 1152921504606846975
	cmp	rax, rcx
	mov	rbx, rcx
	cmovbe	rbx, rax
	sal	rbx, 3
	jmp	.L227
	.p2align 4,,10
	.p2align 3
.L249:
	mov	rdi, QWORD PTR [rsp]
	mov	rdx, r12
	mov	rsi, r14
	mov	QWORD PTR 8[rsp], rax
	call	memcpy@PLT
	mov	rcx, QWORD PTR 8[rsp]
	jmp	.L231
.L247:
	movabs	rax, 1152921504606846975
	cmp	rcx, rax
	cmova	rcx, rax
	lea	rbx, 0[0+rcx*8]
	jmp	.L227
.L245:
	lea	rdi, .LC2[rip]
	call	_ZSt20__throw_length_errorPKc@PLT
	.cfi_endproc
.LFE4084:
	.size	_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_, .-_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_
	.section	.rodata.str1.1
.LC5:
	.string	"true"
.LC6:
	.string	"false"
.LC7:
	.string	"Usage: "
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align 8
.LC8:
	.string	" <N> <offset_floats> <output.csv>\n"
	.section	.rodata.str1.1
.LC9:
	.string	"stoull"
	.section	.rodata.str1.8
	.align 8
.LC10:
	.string	"N must be positive and offset must be 0-15 floats\n"
	.section	.rodata.str1.1
.LC17:
	.string	"Could not open output file: "
.LC18:
	.string	"\n"
	.section	.rodata.str1.8
	.align 8
.LC19:
	.string	"N,offset_floats,runtime_ms,checksum,correct\n"
	.section	.rodata.str1.1
.LC20:
	.string	","
.LC22:
	.string	"N="
.LC23:
	.string	" offset="
.LC24:
	.string	" floats ("
.LC25:
	.string	" bytes)"
.LC26:
	.string	" median_ms="
.LC27:
	.string	" checksum="
.LC28:
	.string	" correct="
	.section	.text.unlikely,"ax",@progbits
.LCOLDB30:
	.section	.text.startup,"ax",@progbits
.LHOTB30:
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB3512:
	.cfi_startproc
	.cfi_personality 0x9b,DW.ref.__gxx_personality_v0
	.cfi_lsda 0x1b,.LLSDA3512
	endbr64
	lea	r10, 8[rsp]
	.cfi_def_cfa 10, 0
	and	rsp, -32
	push	QWORD PTR -8[r10]
	push	rbp
	mov	rbp, rsp
	.cfi_escape 0x10,0x6,0x2,0x76,0
	push	r15
	push	r14
	push	r13
	push	r12
	push	r10
	.cfi_escape 0xf,0x3,0x76,0x58,0x6
	.cfi_escape 0x10,0xf,0x2,0x76,0x78
	.cfi_escape 0x10,0xe,0x2,0x76,0x70
	.cfi_escape 0x10,0xd,0x2,0x76,0x68
	.cfi_escape 0x10,0xc,0x2,0x76,0x60
	push	rbx
	.cfi_escape 0x10,0x3,0x2,0x76,0x50
	mov	rbx, rsi
	sub	rsp, 800
	mov	rax, QWORD PTR fs:40
	mov	QWORD PTR -56[rbp], rax
	xor	eax, eax
	cmp	edi, 4
	je	.L251
	lea	r12, _ZSt4cerr[rip]
	mov	edx, 7
	lea	rsi, .LC7[rip]
	mov	rdi, r12
.LEHB2:
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rsi, QWORD PTR [rbx]
	mov	rdi, r12
	mov	ebx, 1
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
	lea	rsi, .LC8[rip]
	mov	rdi, rax
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
.L250:
	mov	rax, QWORD PTR -56[rbp]
	sub	rax, QWORD PTR fs:40
	jne	.L345
	add	rsp, 800
	mov	eax, ebx
	pop	rbx
	pop	r10
	.cfi_remember_state
	.cfi_def_cfa 10, 0
	pop	r12
	pop	r13
	pop	r14
	pop	r15
	pop	rbp
	lea	rsp, -8[r10]
	.cfi_def_cfa 7, 8
	ret
.L251:
	.cfi_restore_state
	lea	rax, -640[rbp]
	mov	rsi, QWORD PTR 8[rsi]
	lea	r15, -576[rbp]
	mov	rdx, rax
	mov	rdi, r15
	mov	QWORD PTR -776[rbp], r15
	lea	r14, .LC9[rip]
	mov	QWORD PTR -752[rbp], rax
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3_
.LEHE2:
	mov	r8d, 10
	xor	ecx, ecx
	mov	rsi, r14
	mov	r13, QWORD PTR __isoc23_strtoull@GOTPCREL[rip]
	mov	rdx, QWORD PTR -576[rbp]
	mov	rdi, r13
.LEHB3:
	call	_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_
.LEHE3:
	mov	rdi, r15
	mov	r12, rax
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	mov	rsi, QWORD PTR 16[rbx]
	mov	rdx, QWORD PTR -752[rbp]
	mov	rdi, r15
.LEHB4:
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3_
.LEHE4:
	mov	r8d, 10
	xor	ecx, ecx
	mov	rsi, r14
	mov	rdx, QWORD PTR -576[rbp]
	mov	rdi, r13
.LEHB5:
	call	_ZN9__gnu_cxx6__stoaIyycJiEEET0_PFT_PKT1_PPS3_DpT2_EPKcS5_PmS9_
.LEHE5:
	mov	rdi, r15
	mov	r14, rax
	mov	QWORD PTR -744[rbp], rax
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	lea	rcx, -608[rbp]
	mov	rdx, QWORD PTR -752[rbp]
	mov	rsi, QWORD PTR 24[rbx]
	mov	rdi, rcx
	mov	QWORD PTR -808[rbp], rcx
.LEHB6:
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3_
.LEHE6:
	test	r12, r12
	sete	dl
	cmp	r14, 15
	seta	al
	or	dl, al
	mov	BYTE PTR -713[rbp], dl
	jne	.L346
	mov	r13, QWORD PTR -744[rbp]
	lea	r15, 0[r13+r12]
	mov	rdi, r15
.LEHB7:
	call	_Z16allocate_alignedm
	mov	rdi, r15
	mov	QWORD PTR -736[rbp], rax
	mov	r14, rax
	call	_Z16allocate_alignedm
	mov	rdi, r12
	mov	QWORD PTR -728[rbp], rax
	call	_Z16allocate_alignedm
.LEHE7:
	mov	r9, QWORD PTR -728[rbp]
	lea	rcx, 0[0+r13*4]
	mov	r8, r14
	mov	rbx, rax
	lea	r13, [r14+rcx]
	mov	QWORD PTR -816[rbp], rcx
	lea	r14, [r9+rcx]
	test	r15, r15
	je	.L255
	vmovss	xmm4, DWORD PTR .LC11[rip]
	vmovss	xmm3, DWORD PTR .LC12[rip]
	xor	ecx, ecx
	movabs	rdi, -1085102592571150095
	vmovss	xmm2, DWORD PTR .LC13[rip]
	vmovss	xmm1, DWORD PTR .LC14[rip]
	movabs	rsi, 5675921253449092805
	.p2align 4,,10
	.p2align 3
.L256:
	mov	rax, rcx
	vxorps	xmm6, xmm6, xmm6
	mul	rdi
	mov	rax, rdx
	and	rdx, -16
	shr	rax, 4
	add	rdx, rax
	mov	rax, rcx
	sub	rax, rdx
	vcvtsi2ss	xmm0, xmm6, rax
	mov	rax, rcx
	mul	rsi
	vfmadd132ss	xmm0, xmm3, xmm4
	shr	rdx, 2
	lea	rax, [rdx+rdx*2]
	lea	rdx, [rdx+rax*4]
	mov	rax, rcx
	sub	rax, rdx
	vmovss	DWORD PTR [r8+rcx*4], xmm0
	vcvtsi2ss	xmm0, xmm6, rax
	vfmadd132ss	xmm0, xmm1, xmm2
	vmovss	DWORD PTR [r9+rcx*4], xmm0
	add	rcx, 1
	cmp	r15, rcx
	jne	.L256
	cmp	r12, 3
	jbe	.L347
.L255:
	mov	rax, QWORD PTR -816[rbp]
	lea	rdx, 4[rax]
	mov	rax, QWORD PTR -736[rbp]
	lea	rcx, [rax+rdx]
	mov	rax, rbx
	sub	rax, rcx
	cmp	rax, 24
	mov	rax, QWORD PTR -728[rbp]
	seta	cl
	lea	rsi, [rax+rdx]
	mov	rax, rbx
	sub	rax, rsi
	cmp	rax, 24
	seta	al
	and	cl, al
	mov	BYTE PTR -713[rbp], cl
	jne	.L348
	mov	BYTE PTR -713[rbp], 1
.L257:
	xor	eax, eax
	.p2align 4,,10
	.p2align 3
.L263:
	vmovss	xmm0, DWORD PTR 0[r13+rax*4]
	vmulss	xmm0, xmm0, DWORD PTR [r14+rax*4]
	vmovss	DWORD PTR [rbx+rax*4], xmm0
	add	rax, 1
	cmp	rax, r12
	jb	.L263
.L264:
	mov	QWORD PTR -688[rbp], 0x000000000
	xor	eax, eax
	.p2align 4,,10
	.p2align 3
.L265:
	vxorpd	xmm7, xmm7, xmm7
	vcvtss2sd	xmm0, xmm7, DWORD PTR 0[r13+rax*4]
	vcvtss2sd	xmm1, xmm7, DWORD PTR [r14+rax*4]
	vmulsd	xmm0, xmm0, xmm1
	add	rax, 1
	vaddsd	xmm3, xmm0, QWORD PTR -688[rbp]
	vmovsd	QWORD PTR -688[rbp], xmm3
	cmp	rax, r12
	jb	.L265
	mov	QWORD PTR -712[rbp], 0x000000000
	xor	eax, eax
	.p2align 4,,10
	.p2align 3
.L266:
	vxorpd	xmm3, xmm3, xmm3
	vcvtss2sd	xmm0, xmm3, DWORD PTR [rbx+rax*4]
	vaddsd	xmm4, xmm0, QWORD PTR -712[rbp]
	add	rax, 1
	vmovsd	QWORD PTR -712[rbp], xmm4
	cmp	rax, r12
	jb	.L266
	xor	eax, eax
	mov	r15, r12
	vmovsd	xmm6, QWORD PTR -688[rbp]
	vandpd	xmm5, xmm6, XMMWORD PTR .LC15[rip]
	mov	QWORD PTR -656[rbp], rax
	mov	rax, QWORD PTR -728[rbp]
	vpxor	xmm0, xmm0, xmm0
	vmaxsd	xmm7, xmm5, QWORD PTR .LC4[rip]
	vmovdqa	XMMWORD PTR -672[rbp], xmm0
	mov	DWORD PTR -720[rbp], 9
	lea	rcx, [rax+rdx]
	mov	rax, rbx
	sub	rax, rcx
	cmp	rax, 24
	mov	rax, QWORD PTR -736[rbp]
	vmovsd	QWORD PTR -824[rbp], xmm7
	seta	cl
	add	rdx, rax
	mov	rax, rbx
	sub	rax, rdx
	cmp	rax, 24
	seta	al
	shr	r15, 3
	and	ecx, eax
	mov	rax, r12
	sal	r15, 5
	and	rax, -8
	mov	BYTE PTR -714[rbp], cl
	mov	QWORD PTR -784[rbp], rax
	lea	rax, -672[rbp]
	mov	QWORD PTR -760[rbp], rax
	mov	rax, r12
	and	eax, 7
	mov	QWORD PTR -768[rbp], rax
	mov	rax, r12
	and	eax, 7
	mov	QWORD PTR -792[rbp], rax
	sub	rax, 1
	mov	QWORD PTR -800[rbp], rax
	.p2align 4,,10
	.p2align 3
.L279:
	call	_ZNSt6chrono3_V212steady_clock3nowEv@PLT
	mov	rdx, rax
	xor	eax, eax
	cmp	BYTE PTR -713[rbp], 0
	je	.L275
	cmp	BYTE PTR -714[rbp], 0
	jne	.L349
	.p2align 4,,10
	.p2align 3
.L275:
	vmovss	xmm0, DWORD PTR [r14+rax*4]
	vmulss	xmm0, xmm0, DWORD PTR 0[r13+rax*4]
	vmovss	DWORD PTR [rbx+rax*4], xmm0
	add	rax, 1
	cmp	rax, r12
	jb	.L275
.L276:
	mov	QWORD PTR -704[rbp], rdx
	call	_ZNSt6chrono3_V212steady_clock3nowEv@PLT
	mov	rdx, QWORD PTR -704[rbp]
	vxorpd	xmm2, xmm2, xmm2
	mov	rsi, QWORD PTR -664[rbp]
	sub	rax, rdx
	vcvtsi2sd	xmm0, xmm2, rax
	vdivsd	xmm0, xmm0, QWORD PTR .LC16[rip]
	vmovsd	QWORD PTR -640[rbp], xmm0
	cmp	rsi, QWORD PTR -656[rbp]
	je	.L277
	vmovsd	QWORD PTR [rsi], xmm0
	add	rsi, 8
	mov	QWORD PTR -664[rbp], rsi
.L278:
	sub	DWORD PTR -720[rbp], 1
	jne	.L279
	mov	QWORD PTR -704[rbp], 0x000000000
	xor	eax, eax
	.p2align 4,,10
	.p2align 3
.L280:
	vxorpd	xmm1, xmm1, xmm1
	vcvtss2sd	xmm0, xmm1, DWORD PTR [rbx+rax*4]
	vaddsd	xmm3, xmm0, QWORD PTR -704[rbp]
	add	rax, 1
	vmovsd	QWORD PTR -704[rbp], xmm3
	cmp	rax, r12
	jb	.L280
	mov	rsi, QWORD PTR -808[rbp]
	mov	rdi, QWORD PTR -776[rbp]
	mov	edx, 16
.LEHB8:
	call	_ZNSt14basic_ofstreamIcSt11char_traitsIcEEC1ERKNSt7__cxx1112basic_stringIcS1_SaIcEEESt13_Ios_Openmode@PLT
.LEHE8:
	test	BYTE PTR -296[rbp], 5
	jne	.L350
	mov	r15, QWORD PTR -776[rbp]
	lea	rsi, .LC19[rip]
	mov	rdi, r15
.LEHB9:
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
	mov	rsi, r12
	mov	rdi, r15
	call	_ZNSo9_M_insertImEERSoT_@PLT
	lea	r13, .LC20[rip]
	mov	edx, 1
	mov	rdi, rax
	mov	r14, rax
	mov	rsi, r13
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rsi, QWORD PTR -744[rbp]
	mov	rdi, r14
	call	_ZNSo9_M_insertImEERSoT_@PLT
	mov	edx, 1
	mov	rsi, r13
	mov	rdi, rax
	mov	r14, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	r15, QWORD PTR -752[rbp]
	mov	rsi, QWORD PTR -760[rbp]
	mov	rdi, r15
	call	_ZNSt6vectorIdSaIdEEC1ERKS1_
.LEHE9:
	mov	rdi, r15
	call	_Z6medianSt6vectorIdSaIdEE
	mov	rdi, r14
.LEHB10:
	call	_ZNSo9_M_insertIdEERSoT_@PLT
	mov	edx, 1
	mov	rsi, r13
	mov	rdi, rax
	mov	r14, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	vmovsd	xmm0, QWORD PTR -704[rbp]
	mov	rdi, r14
	call	_ZNSo9_M_insertIdEERSoT_@PLT
	mov	edx, 1
	mov	rsi, r13
	mov	rdi, rax
	mov	r14, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	vmovsd	xmm6, QWORD PTR -824[rbp]
	vmulsd	xmm3, xmm6, QWORD PTR .LC21[rip]
	lea	r13, .LC5[rip]
	lea	rax, .LC6[rip]
	vmovsd	xmm7, QWORD PTR -712[rbp]
	vsubsd	xmm0, xmm7, QWORD PTR -688[rbp]
	mov	rdi, r14
	vandpd	xmm1, xmm0, XMMWORD PTR .LC15[rip]
	vmovsd	QWORD PTR -712[rbp], xmm1
	vcomisd	xmm3, xmm1
	vmovsd	QWORD PTR -688[rbp], xmm3
	cmovb	r13, rax
	mov	rsi, r13
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
	lea	r14, .LC18[rip]
	mov	rdi, rax
	mov	rsi, r14
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
.LEHE10:
	mov	rdi, r15
	mov	QWORD PTR -752[rbp], r15
	lea	r15, _ZSt4cout[rip]
	call	_ZNSt6vectorIdSaIdEED1Ev
	mov	edx, 2
	lea	rsi, .LC22[rip]
	mov	rdi, r15
.LEHB11:
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rsi, r12
	mov	rdi, r15
	call	_ZNSo9_M_insertImEERSoT_@PLT
	mov	edx, 8
	lea	rsi, .LC23[rip]
	mov	rdi, rax
	mov	r12, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rsi, QWORD PTR -744[rbp]
	mov	rdi, r12
	call	_ZNSo9_M_insertImEERSoT_@PLT
	mov	edx, 9
	lea	rsi, .LC24[rip]
	mov	rdi, rax
	mov	r12, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rsi, QWORD PTR -816[rbp]
	mov	rdi, r12
	call	_ZNSo9_M_insertImEERSoT_@PLT
	mov	edx, 7
	lea	rsi, .LC25[rip]
	mov	rdi, rax
	mov	r12, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	edx, 11
	lea	rsi, .LC26[rip]
	mov	rdi, r12
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	r15, QWORD PTR -752[rbp]
	mov	rsi, QWORD PTR -760[rbp]
	mov	rdi, r15
	call	_ZNSt6vectorIdSaIdEEC1ERKS1_
.LEHE11:
	mov	rdi, r15
	call	_Z6medianSt6vectorIdSaIdEE
	mov	rdi, r12
.LEHB12:
	call	_ZNSo9_M_insertIdEERSoT_@PLT
	mov	edx, 10
	lea	rsi, .LC27[rip]
	mov	rdi, rax
	mov	r12, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	vmovsd	xmm0, QWORD PTR -704[rbp]
	mov	rdi, r12
	call	_ZNSo9_M_insertIdEERSoT_@PLT
	mov	edx, 9
	lea	rsi, .LC28[rip]
	mov	rdi, rax
	mov	r12, rax
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rsi, r13
	mov	rdi, r12
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
	mov	rdi, rax
	mov	rsi, r14
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
.LEHE12:
	mov	rdi, r15
	call	_ZNSt6vectorIdSaIdEED1Ev
	mov	rdi, QWORD PTR -736[rbp]
	call	free@PLT
	mov	rdi, QWORD PTR -728[rbp]
	call	free@PLT
	mov	rdi, rbx
	xor	ebx, ebx
	call	free@PLT
	vmovsd	xmm3, QWORD PTR -688[rbp]
	vcomisd	xmm3, QWORD PTR -712[rbp]
	setb	bl
.L282:
	mov	rdi, QWORD PTR -776[rbp]
	call	_ZNSt14basic_ofstreamIcSt11char_traitsIcEED1Ev@PLT
	mov	rdi, QWORD PTR -760[rbp]
	call	_ZNSt6vectorIdSaIdEED1Ev
	jmp	.L254
.L346:
	lea	rsi, .LC10[rip]
	lea	rdi, _ZSt4cerr[rip]
.LEHB13:
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
.LEHE13:
	mov	ebx, 1
.L254:
	mov	rdi, QWORD PTR -808[rbp]
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	jmp	.L250
.L348:
	mov	rcx, r12
	cmp	r12, 7
	jbe	.L298
	shr	rcx, 3
	xor	eax, eax
	sal	rcx, 5
	.p2align 4,,10
	.p2align 3
.L259:
	vmovups	ymm2, YMMWORD PTR 0[r13+rax]
	vmulps	ymm0, ymm2, YMMWORD PTR [r14+rax]
	vmovups	YMMWORD PTR [rbx+rax], ymm0
	add	rax, 32
	cmp	rcx, rax
	jne	.L259
	mov	rax, r12
	and	rax, -8
	test	r12b, 7
	je	.L341
	mov	rcx, r12
	sub	rcx, rax
	lea	rsi, -1[rcx]
	cmp	rsi, 2
	jbe	.L351
	vzeroupper
.L258:
	mov	rdi, QWORD PTR -744[rbp]
	lea	rsi, [rax+rdi]
	mov	rdi, QWORD PTR -728[rbp]
	vmovups	xmm4, XMMWORD PTR [rdi+rsi*4]
	mov	rdi, QWORD PTR -736[rbp]
	vmulps	xmm0, xmm4, XMMWORD PTR [rdi+rsi*4]
	mov	rsi, rcx
	vmovaps	XMMWORD PTR -688[rbp], xmm4
	and	rsi, -4
	vmovups	XMMWORD PTR [rbx+rax*4], xmm0
	add	rax, rsi
	and	cl, 3
	je	.L264
.L261:
	vmovss	xmm0, DWORD PTR 0[r13+rax*4]
	vmulss	xmm0, xmm0, DWORD PTR [r14+rax*4]
	lea	rsi, 1[rax]
	lea	rcx, 0[0+rax*4]
	vmovss	DWORD PTR [rbx+rax*4], xmm0
	cmp	rsi, r12
	jnb	.L264
	vmovss	xmm0, DWORD PTR 4[r13+rcx]
	vmulss	xmm0, xmm0, DWORD PTR 4[r14+rcx]
	add	rax, 2
	vmovss	DWORD PTR 4[rbx+rcx], xmm0
	cmp	rax, r12
	jnb	.L264
	vmovss	xmm0, DWORD PTR 8[r13+rcx]
	vmulss	xmm0, xmm0, DWORD PTR 8[r14+rcx]
	vmovss	DWORD PTR 8[rbx+rcx], xmm0
	jmp	.L264
.L347:
	mov	rax, QWORD PTR -816[rbp]
	lea	rdx, 4[rax]
	jmp	.L257
	.p2align 4,,10
	.p2align 3
.L349:
	cmp	r12, 7
	jbe	.L302
	.p2align 4,,10
	.p2align 3
.L271:
	vmovups	ymm5, YMMWORD PTR [r14+rax]
	vmulps	ymm0, ymm5, YMMWORD PTR 0[r13+rax]
	vmovups	YMMWORD PTR [rbx+rax], ymm0
	add	rax, 32
	cmp	rax, r15
	jne	.L271
	cmp	QWORD PTR -768[rbp], 0
	je	.L343
	cmp	QWORD PTR -800[rbp], 2
	mov	rax, QWORD PTR -792[rbp]
	jbe	.L303
	mov	rcx, QWORD PTR -784[rbp]
	vzeroupper
.L270:
	mov	rdi, QWORD PTR -744[rbp]
	lea	rsi, [rcx+rdi]
	mov	rdi, QWORD PTR -728[rbp]
	vmovups	xmm2, XMMWORD PTR [rdi+rsi*4]
	mov	rdi, QWORD PTR -736[rbp]
	vmulps	xmm0, xmm2, XMMWORD PTR [rdi+rsi*4]
	vmovaps	XMMWORD PTR -704[rbp], xmm2
	vmovups	XMMWORD PTR [rbx+rcx*4], xmm0
	test	al, 3
	je	.L276
	and	rax, -4
	add	rax, rcx
.L273:
	vmovss	xmm0, DWORD PTR 0[r13+rax*4]
	vmulss	xmm0, xmm0, DWORD PTR [r14+rax*4]
	lea	rsi, 1[rax]
	lea	rcx, 0[0+rax*4]
	vmovss	DWORD PTR [rbx+rax*4], xmm0
	cmp	rsi, r12
	jnb	.L276
	vmovss	xmm0, DWORD PTR 4[r13+rcx]
	vmulss	xmm0, xmm0, DWORD PTR 4[r14+rcx]
	add	rax, 2
	vmovss	DWORD PTR 4[rbx+rcx], xmm0
	cmp	rax, r12
	jnb	.L276
	vmovss	xmm0, DWORD PTR 8[r14+rcx]
	vmulss	xmm0, xmm0, DWORD PTR 8[r13+rcx]
	vmovss	DWORD PTR 8[rbx+rcx], xmm0
	jmp	.L276
.L277:
	mov	rdx, QWORD PTR -752[rbp]
	mov	rdi, QWORD PTR -760[rbp]
.LEHB14:
	call	_ZNSt6vectorIdSaIdEE17_M_realloc_insertIJRKdEEEvN9__gnu_cxx17__normal_iteratorIPdS1_EEDpOT_
.LEHE14:
	jmp	.L278
.L343:
	vzeroupper
	jmp	.L276
.L302:
	mov	rax, r12
	xor	ecx, ecx
	jmp	.L270
.L303:
	mov	rax, QWORD PTR -784[rbp]
	vzeroupper
	jmp	.L273
.L350:
	lea	r12, _ZSt4cerr[rip]
	mov	edx, 28
	lea	rsi, .LC17[rip]
	mov	rdi, r12
.LEHB15:
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rdx, QWORD PTR -600[rbp]
	mov	rsi, QWORD PTR -608[rbp]
	mov	rdi, r12
	call	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l@PLT
	mov	rdi, rax
	lea	rsi, .LC18[rip]
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@PLT
.LEHE15:
	mov	rdi, QWORD PTR -736[rbp]
	call	free@PLT
	mov	rdi, QWORD PTR -728[rbp]
	call	free@PLT
	mov	rdi, rbx
	mov	ebx, 1
	call	free@PLT
	jmp	.L282
.L341:
	vzeroupper
	jmp	.L264
.L298:
	xor	eax, eax
	jmp	.L258
.L351:
	vzeroupper
	jmp	.L261
.L345:
	call	__stack_chk_fail@PLT
.L311:
	endbr64
	mov	rbx, rax
	jmp	.L291
.L307:
	endbr64
	mov	rbx, rax
	vzeroupper
	jmp	.L293
.L306:
	endbr64
	mov	rbx, rax
	jmp	.L287
.L310:
	endbr64
	mov	rbx, rax
	jmp	.L289
.L309:
	endbr64
	mov	rbx, rax
	vzeroupper
	jmp	.L290
.L308:
	endbr64
	mov	rbx, rax
	vzeroupper
	jmp	.L292
.L305:
	endbr64
	mov	rbx, rax
	jmp	.L285
	.section	.gcc_except_table,"a",@progbits
.LLSDA3512:
	.byte	0xff
	.byte	0xff
	.byte	0x1
	.uleb128 .LLSDACSE3512-.LLSDACSB3512
.LLSDACSB3512:
	.uleb128 .LEHB2-.LFB3512
	.uleb128 .LEHE2-.LEHB2
	.uleb128 0
	.uleb128 0
	.uleb128 .LEHB3-.LFB3512
	.uleb128 .LEHE3-.LEHB3
	.uleb128 .L305-.LFB3512
	.uleb128 0
	.uleb128 .LEHB4-.LFB3512
	.uleb128 .LEHE4-.LEHB4
	.uleb128 0
	.uleb128 0
	.uleb128 .LEHB5-.LFB3512
	.uleb128 .LEHE5-.LEHB5
	.uleb128 .L306-.LFB3512
	.uleb128 0
	.uleb128 .LEHB6-.LFB3512
	.uleb128 .LEHE6-.LEHB6
	.uleb128 0
	.uleb128 0
	.uleb128 .LEHB7-.LFB3512
	.uleb128 .LEHE7-.LEHB7
	.uleb128 .L307-.LFB3512
	.uleb128 0
	.uleb128 .LEHB8-.LFB3512
	.uleb128 .LEHE8-.LEHB8
	.uleb128 .L308-.LFB3512
	.uleb128 0
	.uleb128 .LEHB9-.LFB3512
	.uleb128 .LEHE9-.LEHB9
	.uleb128 .L309-.LFB3512
	.uleb128 0
	.uleb128 .LEHB10-.LFB3512
	.uleb128 .LEHE10-.LEHB10
	.uleb128 .L310-.LFB3512
	.uleb128 0
	.uleb128 .LEHB11-.LFB3512
	.uleb128 .LEHE11-.LEHB11
	.uleb128 .L309-.LFB3512
	.uleb128 0
	.uleb128 .LEHB12-.LFB3512
	.uleb128 .LEHE12-.LEHB12
	.uleb128 .L311-.LFB3512
	.uleb128 0
	.uleb128 .LEHB13-.LFB3512
	.uleb128 .LEHE13-.LEHB13
	.uleb128 .L307-.LFB3512
	.uleb128 0
	.uleb128 .LEHB14-.LFB3512
	.uleb128 .LEHE14-.LEHB14
	.uleb128 .L308-.LFB3512
	.uleb128 0
	.uleb128 .LEHB15-.LFB3512
	.uleb128 .LEHE15-.LEHB15
	.uleb128 .L309-.LFB3512
	.uleb128 0
.LLSDACSE3512:
	.section	.text.startup
	.cfi_endproc
	.section	.text.unlikely
	.cfi_startproc
	.cfi_personality 0x9b,DW.ref.__gxx_personality_v0
	.cfi_lsda 0x1b,.LLSDAC3512
	.type	main.cold, @function
main.cold:
.LFSB3512:
.L291:
	.cfi_escape 0xf,0x3,0x76,0x58,0x6
	.cfi_escape 0x10,0x3,0x2,0x76,0x50
	.cfi_escape 0x10,0x6,0x2,0x76,0
	.cfi_escape 0x10,0xc,0x2,0x76,0x60
	.cfi_escape 0x10,0xd,0x2,0x76,0x68
	.cfi_escape 0x10,0xe,0x2,0x76,0x70
	.cfi_escape 0x10,0xf,0x2,0x76,0x78
	mov	rdi, QWORD PTR -752[rbp]
	vzeroupper
	call	_ZNSt6vectorIdSaIdEED1Ev
.L290:
	mov	rdi, QWORD PTR -776[rbp]
	call	_ZNSt14basic_ofstreamIcSt11char_traitsIcEED1Ev@PLT
.L292:
	mov	rdi, QWORD PTR -760[rbp]
	call	_ZNSt6vectorIdSaIdEED1Ev
.L293:
	mov	rdi, QWORD PTR -808[rbp]
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	mov	rax, QWORD PTR -56[rbp]
	sub	rax, QWORD PTR fs:40
	jne	.L352
	mov	rdi, rbx
.LEHB16:
	call	_Unwind_Resume@PLT
.L287:
	mov	rdi, QWORD PTR -776[rbp]
	vzeroupper
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	mov	rax, QWORD PTR -56[rbp]
	sub	rax, QWORD PTR fs:40
	jne	.L353
	mov	rdi, rbx
	call	_Unwind_Resume@PLT
.L352:
	call	__stack_chk_fail@PLT
.L353:
	call	__stack_chk_fail@PLT
.L289:
	mov	rdi, QWORD PTR -752[rbp]
	vzeroupper
	call	_ZNSt6vectorIdSaIdEED1Ev
	jmp	.L290
.L285:
	mov	rdi, QWORD PTR -776[rbp]
	vzeroupper
	call	_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv@PLT
	mov	rax, QWORD PTR -56[rbp]
	sub	rax, QWORD PTR fs:40
	jne	.L354
	mov	rdi, rbx
	call	_Unwind_Resume@PLT
.LEHE16:
.L354:
	call	__stack_chk_fail@PLT
	.cfi_endproc
.LFE3512:
	.section	.gcc_except_table
.LLSDAC3512:
	.byte	0xff
	.byte	0xff
	.byte	0x1
	.uleb128 .LLSDACSEC3512-.LLSDACSBC3512
.LLSDACSBC3512:
	.uleb128 .LEHB16-.LCOLDB30
	.uleb128 .LEHE16-.LEHB16
	.uleb128 0
	.uleb128 0
.LLSDACSEC3512:
	.section	.text.unlikely
	.section	.text.startup
	.size	main, .-main
	.section	.text.unlikely
	.size	main.cold, .-main.cold
.LCOLDE30:
	.section	.text.startup
.LHOTE30:
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC4:
	.long	0
	.long	1072693248
	.section	.rodata.cst4,"aM",@progbits,4
	.align 4
.LC11:
	.long	1008981770
	.align 4
.LC12:
	.long	1065353216
	.align 4
.LC13:
	.long	1017370378
	.align 4
.LC14:
	.long	1073741824
	.section	.rodata.cst16,"aM",@progbits,16
	.align 16
.LC15:
	.long	-1
	.long	2147483647
	.long	0
	.long	0
	.section	.rodata.cst8
	.align 8
.LC16:
	.long	0
	.long	1093567616
	.align 8
.LC21:
	.long	-1998362383
	.long	1055193269
	.hidden	DW.ref.__gxx_personality_v0
	.weak	DW.ref.__gxx_personality_v0
	.section	.data.rel.local.DW.ref.__gxx_personality_v0,"awG",@progbits,DW.ref.__gxx_personality_v0,comdat
	.align 8
	.type	DW.ref.__gxx_personality_v0, @object
	.size	DW.ref.__gxx_personality_v0, 8
DW.ref.__gxx_personality_v0:
	.quad	__gxx_personality_v0
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
